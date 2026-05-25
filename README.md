# Weather API

A FastAPI weather service powered by [OpenWeatherMap](https://openweathermap.org/) with TTL caching, 5-day forecasts, air quality data, and batch lookups.

## Features

- **Current weather** by city name or lat/lon
- **5-day / 3-hour forecast** with precipitation probability
- **Air Quality Index (AQI)** with full pollutant breakdown
- **Batch lookup** — up to 20 cities in one parallel request
- TTL-based in-memory caching (default 10 min)
- `cached` flag on every response

## Quick Start

```bash
git clone https://github.com/mrnwaiwu/weather-api.git
cd weather-api
pip install -r requirements.txt
cp .env.example .env   # add your OPENWEATHERMAP_API_KEY
uvicorn main:app --reload
```

API docs at `http://localhost:8000/docs`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/weather/{city}` | Current weather by city name |
| GET | `/weather/coords/{lat}/{lon}` | Current weather by coordinates |
| GET | `/forecast/{city}` | 5-day / 3-hour forecast |
| GET | `/air/{city}` | Air quality index (AQI) |
| POST | `/weather/batch` | Bulk weather for up to 20 cities |
| GET | `/cache/stats` | Cache info |
| DELETE | `/cache` | Flush cache |

### Current weather

```bash
curl "http://localhost:8000/weather/Lagos?units=metric"
```

### 5-day forecast

```bash
curl "http://localhost:8000/forecast/Abuja"
```

### Air quality

```bash
curl "http://localhost:8000/air/Lagos"
```

```json
{
  "city": "Lagos",
  "country": "NG",
  "aqi": 2,
  "aqi_label": "Fair",
  "components": { "co": 201.94, "no2": 0.49, "o3": 68.66, "pm2_5": 8.37, "pm10": 10.05 }
}
```

### Batch lookup

```bash
curl -X POST http://localhost:8000/weather/batch \
  -H 'Content-Type: application/json' \
  -d '{"cities": ["Lagos", "Abuja", "London", "Tokyo"], "units": "metric"}'
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENWEATHERMAP_API_KEY` | — | Required. Free key at openweathermap.org |
| `CACHE_TTL_SECONDS` | `600` | Cache lifetime in seconds |
