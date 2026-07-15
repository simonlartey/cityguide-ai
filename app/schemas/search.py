from dataclasses import dataclass
from typing import Any


class SearchValidationError(ValueError):
    """Raised when search request data is invalid."""


@dataclass(frozen=True)
class SearchLocation:
    latitude: float
    longitude: float


@dataclass(frozen=True)
class SearchRequest:
    query: str
    location: SearchLocation | None = None

    @classmethod
    def from_dict(cls, data: Any) -> "SearchRequest":
        if not isinstance(data, dict):
            raise SearchValidationError(
                "Request body must be a JSON object."
            )

        raw_query = data.get("query")

        if not isinstance(raw_query, str):
            raise SearchValidationError(
                "The query field must be a string."
            )

        query = raw_query.strip()

        if not query:
            raise SearchValidationError(
                "Please enter a search query."
            )

        if len(query) > 500:
            raise SearchValidationError(
                "The search query must be 500 characters or fewer."
            )

        raw_location = data.get("location")

        if raw_location is None:
            return cls(query=query)

        if not isinstance(raw_location, dict):
            raise SearchValidationError(
                "The location field must be an object."
            )

        latitude = raw_location.get("latitude")
        longitude = raw_location.get("longitude")

        if isinstance(latitude, bool) or not isinstance(
            latitude,
            (int, float),
        ):
            raise SearchValidationError(
                "Location latitude must be a number."
            )

        if isinstance(longitude, bool) or not isinstance(
            longitude,
            (int, float),
        ):
            raise SearchValidationError(
                "Location longitude must be a number."
            )

        if not -90 <= latitude <= 90:
            raise SearchValidationError(
                "Latitude must be between -90 and 90."
            )

        if not -180 <= longitude <= 180:
            raise SearchValidationError(
                "Longitude must be between -180 and 180."
            )

        return cls(
            query=query,
            location=SearchLocation(
                latitude=float(latitude),
                longitude=float(longitude),
            ),
        )