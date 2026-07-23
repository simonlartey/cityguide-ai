from dataclasses import dataclass
from typing import Any

from app.schemas.search import (
    SearchLocation,
    SearchValidationError,
)


@dataclass(frozen=True)
class DiscoveryRequest:
    location: SearchLocation

    @classmethod
    def from_dict(cls, data: Any) -> "DiscoveryRequest":
        if not isinstance(data, dict):
            raise SearchValidationError(
                "Request body must be a JSON object."
            )

        raw_location = data.get("location")

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
            location=SearchLocation(
                latitude=float(latitude),
                longitude=float(longitude),
            )
        )
