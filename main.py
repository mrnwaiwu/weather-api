from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from cachetools import TTLCache
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Weather API",
    description="Current weather data from OpenWeatherMap with TTL caching",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OWM_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
OWM_BASE_URL = "https://api.openweathermap.org/data/2.5"
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "600"))  # 10 min default

cache: TTLCache = TTLCache(maxsize=200, ttl=CACHE_TTL)


def _parse_owm(data: dict, units: str) -> dict:
    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "icon": data["weather"][0]["icon"],
        "wind_speed": data["wind"]["speed"],
        "units": units,
    }


async def _fetch_owm(params: dict) -> dict:
    if not OWM_API_KEY:
        raise HTTPException(status_code=500, detail="OPENWEATHERMAP_API_KEY not configured")
    params["appid"] = OWM_API_KEY
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{OWM_BASE_URL}/weather", params=params)
    if resp.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid OpenWeatherMap API key")
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Location not found")
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Weather service unavailable")
    return resp.json()


@app.get("/")
async def root():
    return {"message": "Weather API is running", "docs": "/docs"}


@app.get("/weather/{city}")
async def get_weather_by_city(
    city: str,
    units: str = Query("metric", enum=["metric", "imperial", "standard"]),
):
    """Fetch current weather for a city name. Results cached for CACHE_TTL seconds."""
    key = f"city:{city.lower()}:{units}"
    if key in cache:
        return {**cache[key], "cached": True}

    data = await _fetch_owm({"q": city, "units": units})
    result = _parse_owm(data, units)
    cache[key] = result
    return {**result, "cached": False}


@app.get("/weather/coords/{lat}/{lon}")
async def get_weather_by_coords(
    lat: float,
    lon: float,
    units: str = Query("metric", enum=["metric", "imperial", "standard"]),
):
    """Fetch current weather by latitude/longitude."""
    key = f"coords:{lat:.4f}:{lon:.4f}:{units}"
    if key in cache:
        return {**cache[key], "cached": True}

    data = await _fetch_owm({"lat": lat, "lon": lon, "units": units})
    result = _parse_owm(data, units)
    cache[key] = result
    return {**result, "cached": False}


@app.get("/cache/stats")
async def cache_stats():
    """Return current in-memory cache statistics."""
    return {
        "entries": len(cache),
        "max_entries": cache.maxsize,
        "ttl_seconds": CACHE_TTL,
    }


@app.delete("/cache")
async def clear_cache():
    """Manually flush the entire cache."""
    cache.clear()
    return {"message": "Cache cleared"}
