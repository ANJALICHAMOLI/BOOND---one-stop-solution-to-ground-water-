"""Fetch historical rainfall and estimate rooftop harvest potential."""

import json
import math
from datetime import date, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"
HISTORICAL_WEATHER_API_URL = "https://archive-api.open-meteo.com/v1/archive"
WEATHER_DATA_SOURCE = "Open-Meteo Historical Weather API (model-based data)"


def _get_json(url: str, params: dict) -> dict:
    """Request a JSON response and turn network errors into readable errors."""
    request_url = f"{url}?{urlencode(params)}"
    request = Request(request_url, headers={"User-Agent": "Boond/1.0"})

    try:
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Weather service returned HTTP {error.code}: {detail}"
        ) from error
    except (URLError, TimeoutError) as error:
        raise RuntimeError(f"Could not reach the weather service: {error}") from error
    except json.JSONDecodeError as error:
        raise RuntimeError("Weather service returned an invalid JSON response.") from error


def fetch_rainfall_data(location: str, days: int = 30) -> dict:
    """Fetch daily historical rainfall for a named location.

    The default period is the 30 most recent completed calendar days. Open-
    Meteo's geocoder resolves the place name to coordinates, then its
    Historical Weather API returns daily liquid-rain totals for those
    coordinates. This is model-based data, not a reading from a local gauge.

    Args:
        location: City, town, or postal code. Add a region/country to make
            ambiguous place names more specific.
        days: Number of completed calendar days to fetch (1 through 366).

    Returns:
        A dictionary containing the resolved location, daily rainfall in mm,
        period total, data coverage, and source description.

    Raises:
        ValueError: If the location or days value is invalid, or no location
            matches the search.
        RuntimeError: If the weather service cannot be reached or returns
            unusable data.
    """
    if not isinstance(location, str) or not location.strip():
        raise ValueError("location must be a non-empty place name.")
    if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= 366:
        raise ValueError("days must be a whole number between 1 and 366.")

    places = _get_json(
        GEOCODING_API_URL,
        {"name": location.strip(), "count": 1, "language": "en", "format": "json"},
    ).get("results", [])
    if not places:
        raise ValueError(f"No matching location found for {location!r}.")

    place = places[0]
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=days - 1)
    weather = _get_json(
        HISTORICAL_WEATHER_API_URL,
        {
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": "rain_sum",
            "timezone": "auto",
        },
    )

    daily = weather.get("daily") or {}
    dates = daily.get("time") or []
    rain_values = daily.get("rain_sum") or []
    if len(dates) != len(rain_values):
        raise RuntimeError("Weather service returned mismatched rainfall dates and values.")

    daily_rainfall = [
        {"date": day, "rainfall_mm": rainfall}
        for day, rainfall in zip(dates, rain_values)
    ]
    observed_values = [value for value in rain_values if value is not None]
    if not observed_values:
        raise RuntimeError("Weather service returned no rainfall observations for this period.")

    return {
        "location": {
            "name": place.get("name", location.strip()),
            "admin1": place.get("admin1"),
            "country": place.get("country"),
            "latitude": place["latitude"],
            "longitude": place["longitude"],
        },
        "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
        "daily_rainfall": daily_rainfall,
        "total_rainfall_mm": sum(observed_values),
        "days_requested": days,
        "days_with_data": len(observed_values),
        "data_source": WEATHER_DATA_SOURCE,
    }


def estimate_harvestable_water_liters(
    rainfall_mm: float,
    roof_area_m2: float,
    runoff_coefficient: float = 0.8,
) -> float:
    """Estimate harvestable water volume for a rainfall period, in liters.

    One millimeter of rain over one square meter yields one liter before
    losses. The runoff coefficient (between 0 and 1) accounts for water lost
    to absorption, splash, and conveyance. The default is an estimate; users
    should adjust it for their roof and collection system.

    Args:
        rainfall_mm: Rainfall depth for the period, in millimeters.
        roof_area_m2: Horizontal roof catchment area, in square meters.
        runoff_coefficient: Fraction of rainfall expected to reach storage.

    Returns:
        Estimated collectable water volume in liters for the same period.

    Raises:
        ValueError: If an input is not finite, rainfall is negative, roof area
            is not positive, or the runoff coefficient is outside [0, 1].
    """
    values = {
        "rainfall_mm": rainfall_mm,
        "roof_area_m2": roof_area_m2,
        "runoff_coefficient": runoff_coefficient,
    }
    for name, value in values.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number.")

    if rainfall_mm < 0:
        raise ValueError("rainfall_mm cannot be negative.")
    if roof_area_m2 <= 0:
        raise ValueError("roof_area_m2 must be greater than 0.")
    if not 0 <= runoff_coefficient <= 1:
        raise ValueError("runoff_coefficient must be between 0 and 1.")

    return rainfall_mm * roof_area_m2 * runoff_coefficient
