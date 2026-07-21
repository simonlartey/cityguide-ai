from uuid import uuid4

from app.models.search_intent import SearchIntent
from app.providers.assistant.base import AssistantProvider
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
        assistant_provider: AssistantProvider | None = None,
        relevance_ranker: PlaceRelevanceRanker | None = None,
    ):
        self.places_provider = places_provider
        self.assistant_provider = assistant_provider
        self.relevance_ranker = (
            relevance_ranker or PlaceRelevanceRanker()
        )

    def search(self, search_request: SearchRequest) -> dict:
        latitude = None
        longitude = None

        if search_request.location is not None:
            latitude = search_request.location.latitude
            longitude = search_request.location.longitude

        intent = self._parse_search_intent(search_request.query)

        results = self.places_provider.search(
            query=intent.search_query,
            latitude=latitude,
            longitude=longitude,
        )

        ranked_results = self.relevance_ranker.rank(
            query=intent.search_query,
            places=results,
        )

        return {
            "search_id": f"search_{uuid4().hex}",
            "query": search_request.query,
            "result_count": len(ranked_results),
            "results": ranked_results,
        }

    def _parse_search_intent(
        self,
        query: str,
    ) -> SearchIntent:
        if self.assistant_provider is not None:
            return self.assistant_provider.parse_search_intent(query)

        return SearchIntent(
            original_query=query,
            search_query=query,
        )
