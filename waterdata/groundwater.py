"""Find the nearest CGWB groundwater observation to a named location."""

import json
import math
from datetime import datetime
from functools import lru_cache
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PORTAL_API_URL = "https://nwdp.nwic.gov.in/api/3/action"
GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"
NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/search"
DATASET_ID = "gwl-manual-quarterly-central-ground-water-board-department"
SOURCE_NAME = "National Water Data Portal — CGWB Manual Quarterly Ground Water Level"


def _get_json(url: str, params: dict) -> dict:
    """Fetch JSON from a public data service and report useful errors."""
    request_url = f"{url}?{urlencode(params)}"
    request = Request(request_url, headers={"User-Agent": "Boond/1.0"})
    try:
        with urlopen(request, timeout=25) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise RuntimeError(f"Data service returned HTTP {error.code}.") from error
    except (URLError, TimeoutError) as error:
        raise RuntimeError(f"Could not reach a groundwater data service: {error}") from error
    except json.JSONDecodeError as error:
        raise RuntimeError("A groundwater data service returned invalid JSON.") from error
    return payload


def _parse_observation_date(value: str) -> Optional[datetime]:
    for date_format in ("%d-%m-%Y %H:%M", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value.strip(), date_format)
        except (AttributeError, ValueError):
            continue
    return None


@lru_cache(maxsize=256)
def _resolve_location(location: str, state: str) -> dict:
    """Resolve an Indian place to coordinates, with an administrative-area fallback."""
    payload = _get_json(
        GEOCODING_API_URL,
        {
            # Search by locality first: some state names (Delhi in particular)
            # are represented by a longer administrative name in GeoNames.
            "name": location,
            "count": 100,
            "language": "en",
            "format": "json",
            "countryCode": "IN",
        },
    )
    places = payload.get("results") or []
    state_key = " ".join(state.casefold().split())
    state_matches = [
        candidate for candidate in places
        if state_key in " ".join((candidate.get("admin1") or "").casefold().split())
        or (state_key == "delhi" and "delhi" in (candidate.get("admin1") or "").casefold())
    ]
    if state_matches:
        # Exact locality names should sort first, followed by normalized variants.
        location_key = " ".join(location.casefold().split())
        place = next(
            (candidate for candidate in state_matches
             if " ".join(candidate.get("name", "").casefold().split()) == location_key),
            state_matches[0],
        )
        return {
            "name": place.get("name", location),
            "admin1": place.get("admin1") or state,
            "latitude": float(place["latitude"]),
            "longitude": float(place["longitude"]),
            "source": "GeoNames",
        }

    # GeoNames may not list a district as a named place. Use OSM's address
    # search as a fallback for administrative areas such as South Delhi.
    osm_places = _get_json(
        NOMINATIM_API_URL,
        {
            "q": f"{location}, {state}, India",
            "format": "jsonv2",
            "addressdetails": 1,
            "limit": 5,
        },
    )
    if isinstance(osm_places, list):
        for candidate in osm_places:
            address = candidate.get("address") or {}
            administrative_names = " ".join(
                str(address.get(key) or "")
                for key in ("state", "state_district", "county", "city", "region")
            ).casefold()
            display_name = str(candidate.get("display_name") or "").casefold()
            country_code = str(address.get("country_code") or "").casefold()
            if country_code != "in" or (
                state_key not in administrative_names and state_key not in display_name
            ):
                continue
            try:
                return {
                    "name": location,
                    "admin1": address.get("state") or state,
                    "latitude": float(candidate["lat"]),
                    "longitude": float(candidate["lon"]),
                    "source": "OpenStreetMap",
                }
            except (KeyError, TypeError, ValueError):
                continue

    raise ValueError(f"Could not find {location} in {state}. Check the place name and try again.")


@lru_cache(maxsize=48)
def _load_station_observations(resource_id: str) -> tuple:
    """Load a resource once and retain its latest record for each station."""
    observations = {}
    offset = 0
    total = 1
    while offset < total:
        result = _get_json(
            f"{PORTAL_API_URL}/datastore_search",
            {"resource_id": resource_id, "limit": 32000, "offset": offset},
        )
        if not result.get("success"):
            raise RuntimeError("Groundwater data portal could not return station records.")
        data = result.get("result") or {}
        records = data.get("records") or []
        total = data.get("total", len(records))
        for record in records:
            observed_at = _parse_observation_date(record.get("Data Acquisition Time"))
            try:
                latitude = float(record.get("Latitude"))
                longitude = float(record.get("Longitude"))
                depth_m = float(record.get("Groundwater Level Quarterly Manual (meter)"))
            except (TypeError, ValueError):
                continue
            if observed_at is None or not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                continue

            station = record.get("Station") or "CGWB monitoring station"
            key = (station.casefold(), latitude, longitude)
            observation = {
                "station": station,
                "district": record.get("District") or "",
                "latitude": latitude,
                "longitude": longitude,
                "depth_m": depth_m,
                "observed_at": observed_at,
                "agency": record.get("Agency") or "CGWB",
            }
            previous = observations.get(key)
            if previous is None or observed_at > previous["observed_at"]:
                observations[key] = observation

        if not records:
            break
        offset += len(records)
    return tuple(observations.values())


def _distance_km(latitude_a: float, longitude_a: float, latitude_b: float, longitude_b: float) -> float:
    """Calculate straight-line distance between two WGS84 coordinates."""
    lat_a, lat_b = math.radians(latitude_a), math.radians(latitude_b)
    delta_lat = lat_b - lat_a
    delta_lon = math.radians(longitude_b - longitude_a)
    haversine = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat_a) * math.cos(lat_b) * math.sin(delta_lon / 2) ** 2
    )
    return 6371 * 2 * math.atan2(math.sqrt(haversine), math.sqrt(1 - haversine))


def fetch_groundwater_level(state: str, district: str) -> dict:
    """Return the latest observation at the nearest CGWB station in a state.

    The depth is measured at the named CGWB monitoring station. It is not an
    estimate of the user's own well depth or a current sensor reading.
    """
    if not isinstance(state, str) or not state.strip():
        raise ValueError("Enter a state or union territory.")
    if not isinstance(district, str) or not district.strip():
        raise ValueError("Enter a city, district, or locality.")

    state_name = " ".join(state.strip().split())
    location_name = " ".join(district.strip().split())
    place = _resolve_location(location_name, state_name)

    dataset_response = _get_json(f"{PORTAL_API_URL}/package_show", {"id": DATASET_ID})
    if not dataset_response.get("success"):
        raise RuntimeError("Groundwater data portal could not find its CGWB dataset.")
    resources = dataset_response.get("result", {}).get("resources", [])
    resource_prefix = f"Ground Water Level CGWB {state_name} (".casefold()
    state_resources = [
        resource for resource in resources
        if resource.get("name", "").casefold().startswith(resource_prefix)
        and "manual quarterly" in resource.get("name", "").casefold()
        and resource.get("datastore_active")
    ]
    if not state_resources:
        raise ValueError(f"No CGWB groundwater dataset is listed for {state_name}.")

    # Read both the current and prior five-year resources; one may have no data yet.
    observations = []
    for resource in state_resources:
        observations.extend(_load_station_observations(resource["id"]))
    if not observations:
        raise ValueError(f"No CGWB station readings are available for {state_name}.")

    nearest = min(
        observations,
        key=lambda item: _distance_km(
            place["latitude"], place["longitude"], item["latitude"], item["longitude"]
        ),
    )
    distance = _distance_km(
        place["latitude"], place["longitude"], nearest["latitude"], nearest["longitude"]
    )
    return {
        "requested_location": location_name,
        "resolved_location": place["name"],
        "location_source": place["source"],
        "state": state_name,
        "station": nearest["station"],
        "station_district": nearest["district"],
        "distance_km": round(distance, 1),
        "depth_below_ground_m": nearest["depth_m"],
        "observed_at": nearest["observed_at"].strftime("%d %B %Y"),
        "agency": nearest["agency"],
        "data_source": SOURCE_NAME,
        "source_url": "https://nwdp.nwic.gov.in/dataset/gwl-manual-quarterly-central-ground-water-board-department",
    }
