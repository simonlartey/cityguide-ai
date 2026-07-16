from uuid import uuid4

from app.providers.places.base import PlacesProvider
from app.schemas.search import SearchRequest


class SearchService:
    """Coordinate place retrieval and build the search response."""

    def __init__(self, places_provider: PlacesProvider):
        self.places_provider = places_provider

    def search(self, search_request: SearchRequest) -> dict:
        latitude = None
        longitude = None

        if search_request.location is not None:
            latitude = search_request.location.latitude
            longitude = search_request.location.longitude

        results = self.places_provider.search(
            query=search_request.query,
            latitude=latitude,
            longitude=longitude,
        )

        return {
            "search_id": f"search_{uuid4().hex}",
            "query": search_request.query,
            "result_count": len(results),
            "results": results,
        }