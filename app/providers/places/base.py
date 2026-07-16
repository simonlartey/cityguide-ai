from abc import ABC, abstractmethod
from typing import Any


class PlacesProvider(ABC):
    """Interface for place-data providers."""

    @abstractmethod
    def search(
        self,
        query: str,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> list[dict[str, Any]]:
        """Return normalized places matching a search request."""
        raise NotImplementedError