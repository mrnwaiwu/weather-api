# Weather API

A FastAPI weather service that fetches real-time data from [OpenWeatherMap](https://openweathermap.org/) and caches responses in memory with a configurable TTL.

## Features

- Current weather by city name or lat/lon coordinates
- TTL-based in-memory caching (default 10 minutes)
- `cached` flag on every response so you know if data came from cache
- Cache stats and manual flush endpoints
- Supports metric, imperial, and standard units

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/mrnwaiwu/weather-api.git
cd weather-api
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env and set your OpenWeatherMap API key

# 3. Run
uvicorn main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/weather/{city}` | Weather by city name |
| GET | `/weather/coords/{lat}/{lon}` | Weather by coordinates |
| GET | `/cache/stats` | Cache size and TTL info |
| DELETE | `/cache` | Flush the cache |

### Example

```bash
curl http://localhost:8000/weather/Lagos?units=metric
```

```json
{
  "city": "Lagos",
  "country": "NG",
  "temperature": 28.4,
  "feels_like": 32.1,
  "humidity": 78,
  "description": "scattered clouds",
  "wind_speed": 3.6,
  "units": "metric",
  "cached": false
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENWEATHERMAP_API_KEY` | — | Required. Get a free key at openweathermap.org |
| `CACHE_TTL_SECONDS` | `600` | How long to cache each response (seconds) |
