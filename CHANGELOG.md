# Changelog

All notable changes to this project will be documented in this file.

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
