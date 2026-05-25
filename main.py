from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import asyncio
import os
from cachetools import TTLCache
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Weather API",
    description="Current weather, forecasts, air quality, and batch lookups via OpenWeatherMap",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OWM_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
OWM_BASE_URL = "https://api.openweathermap.org/data/2.5"
OWM_GEO_URL  = "http://api.openweathermap.org/geo/1.0"
CACHE_TTL    = int(os.getenv("CACHE_TTL_SECONDS", "600"))  # 10 min default

cache: TTLCache = TTLCache(maxsize=500, ttl=CACHE_TTL)

AQI_LABELS = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_key():
    if not OWM_API_KEY:
        raise HTTPException(status_code=500, detail="OPENWEATHERMAP_API_KEY not configured")


def _parse_current(data: dict, units: str) -> dict:
    return {
        "city":        data["name"],
        "country":     data["sys"]["country"],
        "temperature": data["main"]["temp"],
        "feels_like":  data["main"]["feels_like"],
        "humidity":    data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "icon":        data["weather"][0]["icon"],
        "wind_speed":  data["wind"]["speed"],
        "units":       units,
    }


async def _owm_get(path: str, params: dict) -> dict:
    _require_key()
    params["appid"] = OWM_API_KEY
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(path, params=params)
    if resp.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid OpenWeatherMap API key")
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Location not found")
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Weather service unavailable")
    return resp.json()


async def _geocode(city: str) -> tuple[float, float, str, str]:
    """Return (lat, lon, name, country) for a city string."""
    _require_key()
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{OWM_GEO_URL}/direct",
            params={"q": city, "limit": 1, "appid": OWM_API_KEY},
        )
    if resp.status_code != 200 or not resp.json():
        raise HTTPException(status_code=404, detail=f"City '{city}' not found")
    g = resp.json()[0]
    return g["lat"], g["lon"], g["name"], g.get("country", "")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {"message": "Weather API v2 is running", "docs": "/docs"}


@app.get("/weather/{city}")
async def get_weather_by_city(
    city: str,
    units: str = Query("metric", enum=["metric", "imperial", "standard"]),
):
    """Current weather for a city name."""
    key = f"current:city:{city.lower()}:{units}"
    if key in cache:
        return {**cache[key], "cached": True}
    data   = await _owm_get(f"{OWM_BASE_URL}/weather", {"q": city, "units": units})
    result = _parse_current(data, units)
    cache[key] = result
    return {**result, "cached": False}


@app.get("/weather/coords/{lat}/{lon}")
async def get_weather_by_coords(
    lat: float,
    lon: float,
    units: str = Query("metric", enum=["metric", "imperial", "standard"]),
):
    """Current weather by latitude/longitude."""
    key = f"current:coords:{lat:.4f}:{lon:.4f}:{units}"
    if key in cache:
        return {**cache[key], "cached": True}
    data   = await _owm_get(f"{OWM_BASE_URL}/weather", {"lat": lat, "lon": lon, "units": units})
    result = _parse_current(data, units)
    cache[key] = result
    return {**result, "cached": False}


@app.get("/forecast/{city}")
async def get_forecast(
    city: str,
    units: str = Query("metric", enum=["metric", "imperial", "standard"]),
):
    """5-day / 3-hour forecast for a city (up to 40 data points)."""
    key = f"forecast:{city.lower()}:{units}"
    if key in cache:
        return {**cache[key], "cached": True}

    data = await _owm_get(f"{OWM_BASE_URL}/forecast", {"q": city, "units": units})

    forecasts = [
        {
            "datetime":    item["dt_txt"],
            "temperature": item["main"]["temp"],
            "feels_like":  item["main"]["feels_like"],
            "humidity":    item["main"]["humidity"],
            "description": item["weather"][0]["description"],
            "icon":        item["weather"][0]["icon"],
            "wind_speed":  item["wind"]["speed"],
            "pop":         item.get("pop", 0),  # probability of precipitation
        }
        for item in data["list"]
    ]

    result = {
        "city":      data["city"]["name"],
        "country":   data["city"]["country"],
        "units":     units,
        "forecasts": forecasts,
    }
    cache[key] = result
    return {**result, "cached": False}


@app.get("/air/{city}")
async def get_air_quality(city: str):
    """Air Quality Index (AQI) and pollutant breakdown for a city."""
    key = f"air:{city.lower()}"
    if key in cache:
        return {**cache[key], "cached": True}

    lat, lon, name, country = await _geocode(city)

    data     = await _owm_get(f"{OWM_BASE_URL}/air_pollution", {"lat": lat, "lon": lon})
    entry    = data["list"][0]
    aqi      = entry["main"]["aqi"]

    result = {
        "city":       name,
        "country":    country,
        "lat":        lat,
        "lon":        lon,
        "aqi":        aqi,
        "aqi_label":  AQI_LABELS.get(aqi, "Unknown"),
        "components": entry["components"],
    }
    cache[key] = result
    return {**result, "cached": False}


class BatchRequest(BaseModel):
    cities: list[str]
    units: str = "metric"


@app.post("/weather/batch")
async def get_weather_batch(req: BatchRequest):
    """Fetch current weather for multiple cities in a single parallel request."""
    if not req.cities:
        raise HTTPException(status_code=400, detail="cities list cannot be empty")
    if len(req.cities) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 cities per batch request")

    async def fetch_one(city: str) -> dict:
        key = f"current:city:{city.lower()}:{req.units}"
        if key in cache:
            return {**cache[key], "cached": True, "city_query": city}
        try:
            data   = await _owm_get(f"{OWM_BASE_URL}/weather", {"q": city, "units": req.units})
            result = _parse_current(data, req.units)
            cache[key] = result
            return {**result, "cached": False, "city_query": city}
        except HTTPException as exc:
            return {"city_query": city, "error": exc.detail}

    results = await asyncio.gather(*[fetch_one(c) for c in req.cities])
    return {"units": req.units, "results": list(results)}


# ---------------------------------------------------------------------------
# Cache management
# ---------------------------------------------------------------------------

@app.get("/cache/stats")
async def cache_stats():
    return {"entries": len(cache), "max_entries": cache.maxsize, "ttl_seconds": CACHE_TTL}


@app.delete("/cache")
async def clear_cache():
    cache.clear()
    return {"message": "Cache cleared"}
