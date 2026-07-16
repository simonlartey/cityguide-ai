from datetime import datetime, timedelta, timezone
from math import asin, cos, radians, sin, sqrt
from typing import Any

import requests

from app.providers.places.base import PlacesProvider
from app.providers.places.errors import PlacesProviderError


class GooglePlacesProvider(PlacesProvider):
    """Search Google Places and normalize results for CityGuide."""

    SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

    FIELD_MASK = ",".join(
        (
            "places.id",
            "places.displayName",
            "places.formattedAddress",
            "places.location",
            "places.rating",
            "places.userRatingCount",
            "places.priceLevel",
            "places.currentOpeningHours.openNow",
            "places.regularOpeningHours.weekdayDescriptions",
            "places.utcOffsetMinutes",
            "places.nationalPhoneNumber",
            "places.websiteUri",
            "places.googleMapsUri",
        )
    )

    PRICE_LEVELS = {
        "PRICE_LEVEL_FREE": 1,
        "PRICE_LEVEL_INEXPENSIVE": 1,
        "PRICE_LEVEL_MODERATE": 2,
        "PRICE_LEVEL_EXPENSIVE": 3,
        "PRICE_LEVEL_VERY_EXPENSIVE": 4,
    }

    def __init__(
        self,
        api_key: str,
        timeout_seconds: float = 10,
        session: requests.Session | None = None,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("Google Places API key is required.")

        self.api_key = api_key.strip()
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()

    def search(
        self,
        query: str,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {
            "textQuery": query,
            "pageSize": 10,
        }

        if latitude is not None and longitude is not None:
            payload["locationBias"] = {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                    "radius": 10000.0,
                }
            }

        try:
            response = self.session.post(
                self.SEARCH_URL,
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": self.api_key,
                    "X-Goog-FieldMask": self.FIELD_MASK,
                },
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except requests.RequestException as error:
            raise PlacesProviderError(
                "Google Places search failed."
            ) from error

        try:
            response_data = response.json()
        except ValueError as error:
            raise PlacesProviderError(
                "Google Places returned an invalid response."
            ) from error

        places = response_data.get("places", [])

        if not isinstance(places, list):
            raise PlacesProviderError(
                "Google Places returned malformed place data."
            )

        return [
            self._normalize_place(
                place,
                origin_latitude=latitude,
                origin_longitude=longitude,
            )
            for place in places
            if isinstance(place, dict)
        ]

    def _normalize_place(
        self,
        place: dict[str, Any],
        origin_latitude: float | None = None,
        origin_longitude: float | None = None,
    ) -> dict[str, Any]:
        location = place.get("location") or {}
        display_name = place.get("displayName") or {}
        opening_hours = place.get("currentOpeningHours") or {}
        regular_hours = place.get("regularOpeningHours") or {}
        place_latitude = location.get("latitude")
        place_longitude = location.get("longitude")

        distance_miles = self._calculate_distance_miles(
            origin_latitude=origin_latitude,
            origin_longitude=origin_longitude,
            destination_latitude=place_latitude,
            destination_longitude=place_longitude,
        )

        weekday_descriptions = regular_hours.get(
            "weekdayDescriptions",
            [],
        )

        hours = self._get_current_day_hours(
            weekday_descriptions=weekday_descriptions,
            utc_offset_minutes=place.get(
                "utcOffsetMinutes"
            ),
        )

        rating = place.get("rating")
        review_count = place.get("userRatingCount", 0)
        is_open = opening_hours.get("openNow")

        return {
            "id": place.get("id", ""),
            "name": display_name.get(
                "text",
                "Unnamed place",
            ),
            "category": "Local business",
            "address": place.get(
                "formattedAddress",
                "Address unavailable",
            ),
            "latitude": place_latitude,
            "longitude": place_longitude,
            "rating": rating,
            "review_count": review_count,
            "distance_miles": distance_miles,
            "price_level": self._normalize_price_level(
                place.get("priceLevel")
            ),
            "open_now": is_open,
            "hours_text": hours,
            "description": self._build_description(
                name=display_name.get(
                    "text",
                    "This business",
                ),
                rating=rating,
                review_count=review_count,
            ),
            "tags": self._build_tags(
                rating=rating,
                price_level=place.get("priceLevel"),
                is_open=is_open,
            ),
            "match_reasons": self._build_reasons(
                rating=rating,
                review_count=review_count,
                price_level=place.get("priceLevel"),
            ),
            "phone": place.get("nationalPhoneNumber"),
            "website": place.get("websiteUri"),
            "maps_url": place.get("googleMapsUri"),
        }

    @staticmethod
    def _calculate_distance_miles(
        origin_latitude: float | None,
        origin_longitude: float | None,
        destination_latitude: float | None,
        destination_longitude: float | None,
    ) -> float | None:
        coordinates = (
            origin_latitude,
            origin_longitude,
            destination_latitude,
            destination_longitude,
        )

        if any(coordinate is None for coordinate in coordinates):
            return None

        earth_radius_miles = 3958.8

        origin_latitude_radians = radians(origin_latitude)
        destination_latitude_radians = radians(destination_latitude)

        latitude_difference = radians(
            destination_latitude - origin_latitude
        )
        longitude_difference = radians(
            destination_longitude - origin_longitude
        )

        haversine_value = (
            sin(latitude_difference / 2) ** 2
            + cos(origin_latitude_radians)
            * cos(destination_latitude_radians)
            * sin(longitude_difference / 2) ** 2
        )

        central_angle = 2 * asin(
            sqrt(haversine_value)
        )

        return round(
            earth_radius_miles * central_angle,
            1,
        )

    @staticmethod
    def _get_current_day_hours(
        weekday_descriptions: list[str],
        utc_offset_minutes: int | None,
        current_utc_time: datetime | None = None,
    ) -> str:
        if not weekday_descriptions:
            return "Hours unavailable"

        if utc_offset_minutes is None:
            return weekday_descriptions[0]

        utc_time = current_utc_time or datetime.now(
            timezone.utc
        )

        place_time = utc_time + timedelta(
            minutes=utc_offset_minutes
        )

        current_day_name = place_time.strftime("%A")

        for description in weekday_descriptions:
            day_name, separator, _ = description.partition(":")

            if (
                separator
                and day_name.strip().casefold()
                == current_day_name.casefold()
            ):
                return description

        return "Hours unavailable"

    @staticmethod
    def _build_description(
        name: str,
        rating: float | None,
        review_count: int,
    ) -> str:
        if rating is not None:
            return (
                f"{name} is rated {rating} based on "
                f"{review_count} Google reviews."
            )

        return f"{name} matches your local search."

    @classmethod
    def _build_tags(
        cls,
        rating: float | None,
        price_level: str | None,
        is_open: bool | None,
    ) -> list[str]:
        tags = []

        if rating is not None and rating >= 4.5:
            tags.append("Highly rated")

        normalized_price = cls._normalize_price_level(price_level)

        if normalized_price == 1:
            tags.append("Affordable")
        elif normalized_price == 2:
            tags.append("Moderate price")

        if is_open is True:
            tags.append("Open now")

        if not tags:
            tags.append("Local business")

        return tags

    @classmethod
    def _build_reasons(
        cls,
        rating: float | None,
        review_count: int,
        price_level: str | None,
    ) -> list[str]:
        reasons = []

        if rating is not None:
            reasons.append(
                f"Rated {rating} from {review_count} reviews"
            )

        normalized_price = cls._normalize_price_level(
            price_level
        )

        if normalized_price is not None:
            reasons.append(
                f"Price level: {'$' * normalized_price}"
            )

        if not reasons:
            reasons.append(
                "Matches your local search"
            )

        return reasons

    @classmethod
    def _normalize_price_level(
        cls,
        price_level: str | None,
    ) -> int | None:
        return cls.PRICE_LEVELS.get(price_level)