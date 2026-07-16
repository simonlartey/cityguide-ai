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
            "places.nationalPhoneNumber",
            "places.websiteUri",
            "places.googleMapsUri",
        )
    )

    PRICE_LEVELS = {
        "PRICE_LEVEL_FREE": "$",
        "PRICE_LEVEL_INEXPENSIVE": "$",
        "PRICE_LEVEL_MODERATE": "$$",
        "PRICE_LEVEL_EXPENSIVE": "$$$",
        "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$",
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
            self._normalize_place(place)
            for place in places
            if isinstance(place, dict)
        ]

    def _normalize_place(
        self,
        place: dict[str, Any],
    ) -> dict[str, Any]:
        location = place.get("location") or {}
        display_name = place.get("displayName") or {}
        opening_hours = place.get("currentOpeningHours") or {}
        regular_hours = place.get("regularOpeningHours") or {}

        weekday_descriptions = regular_hours.get(
            "weekdayDescriptions",
            [],
        )

        hours = (
            weekday_descriptions[0]
            if weekday_descriptions
            else "Hours unavailable"
        )

        rating = place.get("rating")
        review_count = place.get("userRatingCount", 0)
        price_level = self.PRICE_LEVELS.get(
            place.get("priceLevel"),
            "Price unavailable",
        )
        is_open = opening_hours.get("openNow")

        return {
            "id": place.get("id", ""),
            "name": display_name.get(
                "text",
                "Unnamed place",
            ),
            "rating": rating,
            "review_count": review_count,
            "distance_miles": None,
            "price_level": price_level,
            "address": place.get(
                "formattedAddress",
                "Address unavailable",
            ),
            "latitude": location.get("latitude"),
            "longitude": location.get("longitude"),
            "is_open": is_open,
            "status": self._format_status(is_open),
            "hours": hours,
            "phone": place.get("nationalPhoneNumber"),
            "website": place.get("websiteUri"),
            "maps_url": place.get("googleMapsUri"),
            "reasons": self._build_reasons(
                rating=rating,
                review_count=review_count,
                price_level=price_level,
            ),
        }

    @staticmethod
    def _format_status(is_open: bool | None) -> str:
        if is_open is True:
            return "Open now"

        if is_open is False:
            return "Closed"

        return "Hours unavailable"

    @staticmethod
    def _build_reasons(
        rating: float | None,
        review_count: int,
        price_level: str,
    ) -> list[str]:
        reasons = []

        if rating is not None:
            reasons.append(
                f"Rated {rating} from {review_count} reviews"
            )

        if price_level != "Price unavailable":
            reasons.append(
                f"Price level: {price_level}"
            )

        if not reasons:
            reasons.append(
                "Matches your local search"
            )

        return reasons