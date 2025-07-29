import json
from json import JSONDecodeError
from os.path import isfile
from shutil import copyfile

import jsonschema

from fw_fanctrl import INTERNAL_RESOURCES_PATH
from fw_fanctrl.Strategy import Strategy
from fw_fanctrl.exception.ConfigurationParsingException import ConfigurationParsingException
from fw_fanctrl.exception.InvalidStrategyException import InvalidStrategyException

VALIDATION_SCHEMA_PATH = INTERNAL_RESOURCES_PATH.joinpath("config.schema.json")
ORIGINAL_CONFIG_PATH = INTERNAL_RESOURCES_PATH.joinpath("config.json")
VALIDATION_SCHEMA = json.load(VALIDATION_SCHEMA_PATH.open("r"))


class Configuration:
    path = None
    data = None

    def __init__(self, path):
        self.path = path
        self.reload()

    def parse(self, raw_config):
        try:
            config = json.loads(raw_config)
            if "$schema" not in config:
                original_config = json.load(ORIGINAL_CONFIG_PATH.open("r"))
                config["$schema"] = original_config["$schema"]
            jsonschema.Draft202012Validator(json.load(VALIDATION_SCHEMA_PATH.open("r"))).validate(config)
            if config["defaultStrategy"] not in config["strategies"]:
                raise ConfigurationParsingException(
                    f"Default strategy '{config["defaultStrategy"]}' is not a valid strategy."
                )
            if config["strategyOnDischarging"] != "" and config["strategyOnDischarging"] not in config["strategies"]:
                raise ConfigurationParsingException(
                    f"Discharging strategy '{config['strategyOnDischarging']}' is not a valid strategy."
                )
            return config
        except JSONDecodeError as e:
            raise ConfigurationParsingException(f"Error parsing configuration file: {e}")

    def reload(self):
        if not isfile(self.path):
            copyfile(ORIGINAL_CONFIG_PATH, self.path)
        with open(self.path, "r") as fp:
            raw_config = fp.read()
        self.data = self.parse(raw_config)

    def save(self):
        string_config = json.dumps(self.data, indent=4)
        with open(self.path, "w") as fp:
            fp.write(string_config)

    def get_strategies(self):
        return self.data["strategies"].keys()

    def get_strategy(self, strategy_name):
        if strategy_name == "strategyOnDischarging":
            strategy_name = self.data[strategy_name]
            if strategy_name == "":
                strategy_name = "defaultStrategy"
        if strategy_name == "defaultStrategy":
            strategy_name = self.data[strategy_name]
        if strategy_name is None or strategy_name not in self.data["strategies"]:
            raise InvalidStrategyException(strategy_name)
        return Strategy(strategy_name, self.data["strategies"][strategy_name])

    def get_default_strategy(self):
        return self.get_strategy("defaultStrategy")

    def get_discharging_strategy(self):
        return self.get_strategy("strategyOnDischarging")

    def coerce_strategy_param(self, strategy_name, param, value):
        """Coerce a parameter value according to the schema."""
        if strategy_name not in self.data["strategies"]:
            raise InvalidStrategyException(strategy_name)

        strategy_schema = VALIDATION_SCHEMA["$defs"]["strategy"]["properties"]
        if param not in strategy_schema:
            raise ConfigurationParsingException(f"Unknown parameter '{param}' for strategy '{strategy_name}'")

        expected_type = strategy_schema[param].get("type")

        try:
            if expected_type == "boolean":
                if isinstance(value, str):
                    if value.lower() in ("true", "1", "yes", "on"):
                        return True
                    if value.lower() in ("false", "0", "no", "off"):
                        return False
                    raise ValueError
                return bool(value)
            if expected_type == "integer":
                return int(value)
            if expected_type == "number":
                return float(value)
            if expected_type == "array":
                raise ConfigurationParsingException(f"Editing list parameter '{param}' is not supported via CLI")
            return str(value)
        except (TypeError, ValueError) as e:
            raise ConfigurationParsingException(f"Invalid value for '{param}': {value}") from e

    def update_strategy_param(self, strategy_name, param, value):
        """Update a single strategy parameter with schema validation."""
        coerced = self.coerce_strategy_param(strategy_name, param, value)
        strategy = self.data["strategies"][strategy_name]
        old_value = strategy.get(param)
        strategy[param] = coerced

        try:
            jsonschema.validate(self.data, VALIDATION_SCHEMA)
        except jsonschema.ValidationError as e:
            strategy[param] = old_value
            raise ConfigurationParsingException(f"Schema violation: {e.message}") from e

        self.save()
