# Query Parameters Reference

Complete reference for all supported query parameters across weather-api endpoints.

## Common Parameters

These parameters are accepted by all endpoints:

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `units` | string | No | `metric` | Unit system: `metric`, `imperial`, or `standard` |
| `lang` | string | No | `en` | Response language (ISO 639-1 code) |

## `/current` — Current Conditions

**GET** `/current`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `city` | string | Yes* | City name (e.g. `London`) |
| `lat` | float | Yes* | Latitude (-90 to 90) |
| `lon` | float | Yes* | Longitude (-180 to 180) |
| `zip` | string | Yes* | ZIP/postal code with country (e.g. `10001,us`) |

*One of `city`, `lat`+`lon`, or `zip` is required.

### Example

```
GET /current?city=Lagos&units=metric
```

### Response Fields

```json
{
  "temp": 31.2,
  "feels_like": 34.8,
  "humidity": 78,
  "wind_speed": 4.1,
  "wind_deg": 220,
  "uv_index": 9.3,
  "description": "partly cloudy",
  "units": "metric"
}
```

---

## `/forecast` — Multi-Day Forecast

**GET** `/forecast`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `city` | string | Yes* | — | City name |
| `lat` | float | Yes* | — | Latitude |
| `lon` | float | Yes* | — | Longitude |
| `days` | integer | No | `7` | Forecast horizon: 1–14 days |
| `granularity` | string | No | `daily` | `daily` or `hourly` |

### Example

```
GET /forecast?city=London&days=5&granularity=hourly&units=imperial
```

---

## `/alerts` — Weather Alerts

**GET** `/alerts`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `lat` | float | Yes | Latitude |
| `lon` | float | Yes | Longitude |

Returns active National Weather Service alerts for the given coordinates.

---

## Units Reference

| Measurement | `metric` | `imperial` | `standard` |
|---|---|---|---|
| Temperature | °C | °F | K |
| Wind speed | m/s | mph | m/s |
| Pressure | hPa | hPa | hPa |

---

## Rate Limits

- **Free tier:** 60 requests/minute
- **Pro tier:** 600 requests/minute

Rate limit headers are included in every response:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 47
X-RateLimit-Reset: 1749340800
```
