from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from fastapi import HTTPException

from backend.services.facility_service import load_facilities


INDIA_LATITUDE_RANGE = (6.0, 38.0)
INDIA_LONGITUDE_RANGE = (68.0, 98.0)
MAPBOX_GEOCODING_URL = "https://api.mapbox.com/search/geocode/v6/forward"


def get_facility_map(facility_id: str) -> dict[str, Any]:
    facility = find_facility(facility_id)
    name = str(facility.get("name") or "Unknown facility")
    address = build_address(facility)
    latitude, longitude = extract_coordinates(facility)

    if coordinates_are_in_india(latitude, longitude):
        return build_response(
            facility_id=facility_id,
            name=name,
            address=address,
            latitude=latitude,
            longitude=longitude,
            source="existing_coordinates",
            confidence="high",
            place_name=address,
            warning=None,
        )

    token = os.getenv("MAPBOX_TOKEN")
    if not token:
        warning = "No reliable map location found because MAPBOX_TOKEN is not configured."
        if latitude is not None and longitude is not None:
            warning = "Existing coordinates are outside the expected India bounds and MAPBOX_TOKEN is not configured for geocoding."

        return build_response(
            facility_id=facility_id,
            name=name,
            address=address,
            latitude=None,
            longitude=None,
            source="unavailable",
            confidence="low",
            place_name=None,
            warning=warning,
        )

    geocoded = geocode_facility(facility, token)
    if geocoded:
        return build_response(
            facility_id=facility_id,
            name=name,
            address=address,
            latitude=geocoded["latitude"],
            longitude=geocoded["longitude"],
            source="mapbox_geocoded",
            confidence="medium",
            place_name=geocoded["placeName"],
            warning="Coordinates were geocoded from facility name/address and should be manually verified.",
        )

    return build_response(
        facility_id=facility_id,
        name=name,
        address=address,
        latitude=None,
        longitude=None,
        source="unavailable",
        confidence="low",
        place_name=None,
        warning="No reliable map location found from existing data or Mapbox geocoding.",
    )


def find_facility(facility_id: str) -> dict[str, Any]:
    facility = next(
        (item for item in load_facilities() if item.get("facility_id") == facility_id),
        None,
    )
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility


def build_address(facility: dict[str, Any]) -> str:
    parts = [
        facility.get("name"),
        facility.get("address_city"),
        facility.get("address_stateOrRegion"),
        facility.get("address_zipOrPostcode"),
        facility.get("address_country") or "India",
    ]
    return ", ".join(str(part).strip() for part in parts if str(part or "").strip())


def build_geocode_query(facility: dict[str, Any]) -> str:
    parts = [
        facility.get("name"),
        facility.get("address_city"),
        facility.get("address_stateOrRegion"),
        "India",
    ]
    return ", ".join(str(part).strip() for part in parts if str(part or "").strip())


def extract_coordinates(facility: dict[str, Any]) -> tuple[float | None, float | None]:
    latitude = first_float_value(facility, ["latitude", "lat"])
    longitude = first_float_value(facility, ["longitude", "lng", "lon"])
    return latitude, longitude


def first_float_value(facility: dict[str, Any], keys: list[str]) -> float | None:
    for key in keys:
        value = facility.get(key)
        if value is None or value == "":
            continue

        try:
            return float(str(value).strip())
        except ValueError:
            continue

    return None


def coordinates_are_in_india(
    latitude: float | None,
    longitude: float | None,
) -> bool:
    if latitude is None or longitude is None:
        return False

    return (
        INDIA_LATITUDE_RANGE[0] <= latitude <= INDIA_LATITUDE_RANGE[1]
        and INDIA_LONGITUDE_RANGE[0] <= longitude <= INDIA_LONGITUDE_RANGE[1]
    )


def geocode_facility(
    facility: dict[str, Any],
    token: str,
) -> dict[str, Any] | None:
    query = build_geocode_query(facility)
    if not query:
        return None

    params = urlencode(
        {
            "q": query,
            "country": "IN",
            "limit": 1,
            "autocomplete": "false",
            "access_token": token,
        }
    )
    url = f"{MAPBOX_GEOCODING_URL}?{params}"

    try:
        with urlopen(url, timeout=6) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return None

    features = payload.get("features") or []
    if not features:
        return None

    feature = features[0]
    coordinates = (feature.get("geometry") or {}).get("coordinates") or []
    if len(coordinates) < 2:
        return None

    longitude = float(coordinates[0])
    latitude = float(coordinates[1])
    if not coordinates_are_in_india(latitude, longitude):
        return None

    properties = feature.get("properties") or {}
    place_name = (
        properties.get("full_address")
        or properties.get("place_formatted")
        or properties.get("name")
        or feature.get("place_name")
    )

    return {
        "latitude": latitude,
        "longitude": longitude,
        "placeName": place_name,
    }


def build_response(
    facility_id: str,
    name: str,
    address: str | None,
    latitude: float | None,
    longitude: float | None,
    source: str,
    confidence: str,
    place_name: str | None,
    warning: str | None,
) -> dict[str, Any]:
    return {
        "facilityId": facility_id,
        "name": name,
        "address": address,
        "latitude": latitude,
        "longitude": longitude,
        "source": source,
        "confidence": confidence,
        "placeName": place_name,
        "warning": warning,
    }
