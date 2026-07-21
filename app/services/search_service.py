from uuid import uuid4

from app.providers.places.base import PlacesProvider
from app.schemas.search import SearchRequest
from app.services.place_relevance_ranker import (
    PlaceRelevanceRanker,
)


class SearchService:
    """Coordinate place retrieval, ranking, and response creation."""

    def __init__(
        self,
        places_provider: PlacesProvider,
        relevance_ranker: PlaceRelevanceRanker | None = None,
    ):
        self.places_provider = places_provider
        self.relevance_ranker = (
            relevance_ranker or PlaceRelevanceRanker()
        )

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

        ranked_results = self.relevance_ranker.rank(
            query=search_request.query,
            places=results,
        )

        return {
            "search_id": f"search_{uuid4().hex}",
            "query": search_request.query,
            "result_count": len(ranked_results),
            "results": ranked_results,
        }
