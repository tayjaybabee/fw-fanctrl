Sure! Here's a full-featured, user-friendly Markdown documentation page for your new feature: `temperaturePollingInterval`.

---

# 🔧 `temperaturePollingInterval` — Reduce EC Load with Smarter Temperature Polling

Framework laptops use EC (Embedded Controller) queries to read temperature data, which can be resource-sensitive.
With the addition of `temperaturePollingInterval`, you now have **fine-grained control** over how often temperatures are read — **independent from how often fan speed is updated**.

---

## ✨ What Is It?

`temperaturePollingInterval` is a new configuration option in each strategy that defines how often (in seconds) the EC is queried for a fresh temperature reading.

By default, fan speed and temperature were both checked once per second. Now, with this setting, you can **reduce polling frequency**, which:

* ✅ Decreases EC overhead
* ✅ Reduces system jitter or fan controller instability
* ✅ Helps battery life slightly when on DC

---

## ⚙️ Where Does It Go?

This is a **per-strategy setting**, defined in your `config.json` like this:

```json
{
  "defaultStrategy": "balanced",
  "strategyOnDischarging": "quiet",
  "strategies": {
    "balanced": {
      "fanSpeedUpdateFrequency": 3,
      "movingAverageInterval": 30,
      "temperaturePollingInterval": 3,
      "speedCurve": [
        { "temp": 40, "speed": 0 },
        { "temp": 70, "speed": 100 }
      ]
    }
  },
  "$schema": "./config.schema.json"
}
```

---

## 📐 How Does It Work?

### Before:

```python
get_actual_temperature()  # Called every second
adapt_speed(temp)         # Called every fanSpeedUpdateFrequency
```

### Now:

* The EC is queried only **once every `temperaturePollingInterval` seconds**
* That value is **cached** between reads
* Fan speed is still updated independently

---

## 🧪 Example Use Cases

### 🔇 Quiet Mode

```json
"quiet": {
  "fanSpeedUpdateFrequency": 10,
  "movingAverageInterval": 60,
  "temperaturePollingInterval": 5,
  ...
}
```

> Great for reducing noise and EC spam while on battery.

---

### 🐝 Aggressive Mode

```json
"performance": {
  "fanSpeedUpdateFrequency": 2,
  "movingAverageInterval": 10,
  "temperaturePollingInterval": 1,
  ...
}
```

> Keeps your system cool and responsive at the cost of more EC interaction.

---

## 🧑‍💻 Runtime Modification (CLI)

You can change this without editing the file manually:

```bash
fw-fanctrl set_strategy_param balanced temperaturePollingInterval 5
```

This:

* Updates `config.json`
* Reloads the strategy live if it's active
* Persists across reboots

---

## 📏 Constraints & Schema

* Type: `integer`
* Range: `1–60` seconds
* Optional (defaults to `1` if missing)

Defined in schema as:

```json
"temperaturePollingInterval": {
  "type": "integer",
  "minimum": 1,
  "maximum": 60,
  "description": "How often (in seconds) to query the EC for temperature. Reduces load on EC."
}
```

---

## 📝 Recommendations

| Scenario               | Recommended Interval           |
| ---------------------- | ------------------------------ |
| On battery (quiet)     | 5–10 seconds                   |
| Light daily use        | 3–5 seconds                    |
| Gaming / performance   | 1–2 seconds                    |
| Benchmarking / testing | 1 second (minimum allowed) |

---

## 🧠 TL;DR

* Add `"temperaturePollingInterval": X` in your strategy block
* Avoids hammering the EC every second
* Keeps your Framework system calm, cool, and stable 🧊

---

Let me know if you want a badge, diagram, or animated example showing polling vs fan updating visually!
