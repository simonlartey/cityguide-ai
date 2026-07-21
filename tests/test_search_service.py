from app.models.search_intent import SearchIntent
from app.schemas.search import SearchLocation, SearchRequest
from app.services.search_service import SearchService


class RecordingPlacesProvider:
    """Test provider that records the arguments it receives."""

    def __init__(self):
        self.received_query = None
        self.received_latitude = None
        self.received_longitude = None

    def search(
        self,
        query: str,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> list[dict]:
        self.received_query = query
        self.received_latitude = latitude
        self.received_longitude = longitude

        return [
            {
                "id": "test-place",
                "name": "Test Place",
            }
        ]


class StaticPlacesProvider:
    """Return a predefined collection of places."""

    def __init__(self, places: list[dict]):
        self.places = places

    def search(
        self,
        query: str,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> list[dict]:
        return self.places


class RecordingAssistantProvider:
    """Test assistant provider that records and rewrites query intent."""

    def __init__(self):
        self.received_query = None
        self.response_query = None
        self.response_places = None

    def parse_search_intent(
        self,
        query: str,
    ) -> SearchIntent:
        self.received_query = query

        return SearchIntent(
            original_query=query,
            search_query="quiet cafe",
        )

    def generate_search_response(
        self,
        query: str,
        places: list[dict],
    ) -> str:
        self.response_query = query
        self.response_places = places

        return "Campus Cafe is the strongest match."


def test_search_service_returns_expected_response():
    provider = RecordingPlacesProvider()
    service = SearchService(provider)

    response = service.search(
        SearchRequest(query="Quiet coffee shop")
    )

    assert response["query"] == "Quiet coffee shop"
    assert response["result_count"] == 1
    assert response["results"] == [
        {
            "id": "test-place",
            "name": "Test Place",
        }
    ]
    assert response["search_id"].startswith("search_")


def test_search_service_passes_query_to_provider():
    provider = RecordingPlacesProvider()
    service = SearchService(provider)

    service.search(
        SearchRequest(query="Affordable barber")
    )

    assert provider.received_query == "Affordable barber"
    assert provider.received_latitude is None
    assert provider.received_longitude is None


def test_search_service_passes_location_to_provider():
    provider = RecordingPlacesProvider()
    service = SearchService(provider)

    service.search(
        SearchRequest(
            query="Study space",
            location=SearchLocation(
                latitude=43.6591,
                longitude=-70.2568,
            ),
        )
    )

    assert provider.received_query == "Study space"
    assert provider.received_latitude == 43.6591
    assert provider.received_longitude == -70.2568


def test_search_service_handles_empty_provider_results():
    class EmptyPlacesProvider:
        def search(
            self,
            query: str,
            latitude: float | None = None,
            longitude: float | None = None,
        ) -> list[dict]:
            return []

    service = SearchService(EmptyPlacesProvider())

    response = service.search(
        SearchRequest(query="Rare local service")
    )

    assert response["result_count"] == 0
    assert response["results"] == []


def test_search_service_generates_unique_search_ids():
    provider = RecordingPlacesProvider()
    service = SearchService(provider)

    first_response = service.search(
        SearchRequest(query="Coffee")
    )
    second_response = service.search(
        SearchRequest(query="Coffee")
    )

    assert first_response["search_id"] != second_response["search_id"]


def test_search_service_returns_results_in_relevance_order():
    provider = StaticPlacesProvider(
        [
            {
                "id": "popular-grill",
                "name": "Popular Downtown Grill",
                "category": "Restaurant",
                "primary_type": "restaurant",
                "types": [
                    "restaurant",
                    "food",
                ],
                "rating": 4.9,
                "review_count": 2400,
                "distance_miles": 0.2,
            },
            {
                "id": "lagos-kitchen",
                "name": "Lagos Kitchen",
                "category": "African restaurant",
                "primary_type": "african_restaurant",
                "types": [
                    "african_restaurant",
                    "restaurant",
                    "food",
                ],
                "rating": 4.5,
                "review_count": 180,
                "distance_miles": 1.3,
            },
        ]
    )
    service = SearchService(provider)

    response = service.search(
        SearchRequest(
            query="African restaurant near me"
        )
    )

    assert [
        place["id"]
        for place in response["results"]
    ] == [
        "lagos-kitchen",
        "popular-grill",
    ]


def test_search_service_reports_count_after_ranking():
    provider = StaticPlacesProvider(
        [
            {
                "id": "first-place",
                "name": "First Place",
            },
            {
                "id": "second-place",
                "name": "Second Place",
            },
        ]
    )
    service = SearchService(provider)

    response = service.search(
        SearchRequest(query="restaurant")
    )

    assert response["result_count"] == 2


def test_search_service_parses_query_with_assistant_provider():
    places_provider = RecordingPlacesProvider()
    assistant_provider = RecordingAssistantProvider()

    service = SearchService(
        places_provider=places_provider,
        assistant_provider=assistant_provider,
    )

    service.search(
        SearchRequest(query="Find somewhere quiet to study")
    )

    assert assistant_provider.received_query == (
        "Find somewhere quiet to study"
    )


def test_search_service_uses_intent_search_query_for_places():
    places_provider = RecordingPlacesProvider()
    assistant_provider = RecordingAssistantProvider()

    service = SearchService(
        places_provider=places_provider,
        assistant_provider=assistant_provider,
    )

    response = service.search(
        SearchRequest(query="Find somewhere quiet to study")
    )

    assert places_provider.received_query == "quiet cafe"
    assert response["query"] == "Find somewhere quiet to study"


def test_search_service_generates_response_from_ranked_places():
    places_provider = StaticPlacesProvider(
        [
            {
                "id": "popular-grill",
                "name": "Popular Downtown Grill",
                "category": "Restaurant",
                "primary_type": "restaurant",
                "types": [
                    "restaurant",
                    "food",
                ],
            },
            {
                "id": "lagos-kitchen",
                "name": "Lagos Kitchen",
                "category": "African restaurant",
                "primary_type": "african_restaurant",
                "types": [
                    "african_restaurant",
                    "restaurant",
                    "food",
                ],
            },
        ]
    )
    assistant_provider = RecordingAssistantProvider()

    service = SearchService(
        places_provider=places_provider,
        assistant_provider=assistant_provider,
    )

    response = service.search(
        SearchRequest(query="African restaurant near me")
    )

    assert assistant_provider.response_query == (
        "African restaurant near me"
    )
    assert [
        place["id"]
        for place in assistant_provider.response_places
    ] == [
        "lagos-kitchen",
        "popular-grill",
    ]
    assert response["assistant_response"] == (
        "Campus Cafe is the strongest match."
    )


def test_search_service_returns_no_assistant_response_without_provider():
    service = SearchService(
        RecordingPlacesProvider()
    )

    response = service.search(
        SearchRequest(query="Coffee")
    )

    assert response["assistant_response"] is None
