class Strategy:
    name = None
    fan_speed_update_frequency = None
    moving_average_interval = None
    speed_curve = None

    def __init__(self, name, parameters):
        self.name = name

        self.fan_speed_update_frequency = parameters["fanSpeedUpdateFrequency"]

        if self.fan_speed_update_frequency is None or self.fan_speed_update_frequency == "":
            self.fan_speed_update_frequency = 5

        self.moving_average_interval = parameters["movingAverageInterval"]

        if self.moving_average_interval is None or self.moving_average_interval == "":
            self.moving_average_interval = 20

        self.temperature_polling_interval = parameters.get("temperaturePollingInterval", 1) or 1

        self.speed_curve = parameters["speedCurve"]

    def to_dict(self):
        return {
            "fanSpeedUpdateFrequency": self.fan_speed_update_frequency,
            "movingAverageInterval": self.moving_average_interval,
            "temperaturePollingInterval": self.temperature_polling_interval,
            "speedCurve": self.speed_curve
        }
