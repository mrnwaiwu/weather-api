# Changelog

All notable changes to this project will be documented in this file.

## 2026-07-12 - Minor improvements

- Added `heat_index_category` field to `/current` endpoint response (safe/caution/danger/extreme)
- Improved severe weather alert deduplication when multiple overlapping advisories are active
- Fixed timezone rollover bug that shifted sunrise/sunset times by one day near the International Date Line
- Added `precip_type` field (rain/snow/sleet/freezing) to hourly forecast periods

## 2026-06-29 - Minor improvements

- Added `moon_phase` field to `/forecast` endpoint response for astronomy-aware clients
- Improved pollen count integration with regional allergen data providers
- Fixed edge case where tropical storm alerts were not propagated to affected coastal zones
- Added `feels_like_night` field to overnight forecast periods for improved comfort scoring

## 2026-06-26 - Minor improvements

- Added `visibility` field (km/miles) to `/current` endpoint response
- Improved storm alert integration to include NWS advisory severity levels
- Fixed race condition in concurrent forecast cache refresh under high load
- Added `dew_point` field to hourly forecast to support comfort index calculations

## 2026-06-22 - Minor improvements

- Added `pressure_trend` field to `/current` endpoint response (rising/falling/steady)
- Improved forecast accuracy for mountainous regions with elevation-adjusted temperature modeling
- Fixed bug where `lang=es` parameter occasionally returned English condition descriptions
- Added response compression (gzip) for `/forecast` endpoint to reduce payload size

## 2026-06-18 - Minor improvements

- Added `air_quality` index field to `/current` endpoint response
- Improved forecast confidence scoring for rapidly changing frontal systems
- Fixed incorrect "feels like" temperature when wind chill and heat index overlap
- Added retry-with-backoff for transient upstream provider timeouts

## 2026-06-15 - Minor improvements

- Added sunset/sunrise times to `/current` endpoint response
- Improved precipitation probability calculation for coastal regions
- Fixed edge case where negative humidity values appeared in dry desert zones
- Added `lang` query parameter for localized weather condition descriptions

## 2026-06-08 - Minor improvements

- Added wind speed and direction fields to `/current` endpoint response
- Improved UV index calculation accuracy for high-altitude locations
- Fixed response caching bug that occasionally served stale data after TTL expiry
- Added `units` query parameter support for imperial/metric toggling per request

## 2026-06-04 - Minor improvements

- Added support for hourly forecast granularity in `/forecast` endpoint
- Improved geolocation fallback when city name lookup returns ambiguous results
- Fixed off-by-one error in 7-day forecast date range calculation
- Added `X-Cache-Status` response header to indicate cache hit/miss

## 2026-06-01 - Minor improvements

- Added caching layer for frequently requested city forecasts
- Improved rate limiting response headers (X-RateLimit-Remaining)
- Fixed timezone offset calculation for southern hemisphere locations
- Updated API docs with new query parameter examples

## 2026-05-29 - Minor improvements

- Refactored weather data parsing for improved accuracy
- Added input validation for location query parameters
- Improved error messages for unsupported regions
- Minor code cleanup and formatting

## 2026-05-01 - Initial release

- Basic weather API endpoints: current conditions, forecast
- Support for city name and coordinates queries
- JSON response formatting
