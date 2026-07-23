from typing import Any

from app.providers.places.base import PlacesProvider
from app.schemas.discovery import DiscoveryRequest
from app.schemas.search import SearchLocation
from app.services.discovery_service import (
    DiscoveryService,
)


class DiscoveryTestPlacesProvider(PlacesProvider):
    def search(
        self,
        query: str,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> list[dict[str, Any]]:
        return [
            {
                "id": "place-1",
                "name": "Place One",
                "category": "Cafe",
                "photos": [
                    {
                        "name": "places/a/photos/1",
                    }
                ],
            },
            {
                "id": "place-2",
                "name": "Place Two",
                "category": "Restaurant",
                "photos": [
                    {
                        "name": "places/b/photos/2",
                    }
                ],
            },
            {
                "id": "place-3",
                "name": "Place Three",
                "category": "Park",
                "photos": [
                    {
                        "name": "places/c/photos/3",
                    }
                ],
            },
            {
                "id": "place-4",
                "name": "Place Four",
                "category": "Gallery",
                "photos": [
                    {
                        "name": "places/d/photos/4",
                    }
                ],
            },
        ]


def test_discovery_service_returns_grouped_places():
    service = DiscoveryService(
        places_provider=DiscoveryTestPlacesProvider()
    )

    response = service.discover(
        DiscoveryRequest(
            location=SearchLocation(
                latitude=43.6591,
                longitude=-70.2568,
            )
        )
    )

    assert len(response["sections"]) == 3

    assert response["sections"][0]["id"] == (
        "trending"
    )

    assert response["sections"][0]["title"] == (
        "Trending Near You"
    )

    assert response["sections"][0][
        "description"
    ] == "See what is trending right now."

    assert response["sections"][1]["id"] == (
        "students"
    )

    assert response["sections"][2]["id"] == (
        "hidden-gems"
    )

    assert len(response["moods"]) == 4

    assert [
        mood["id"] for mood in response["moods"]
    ] == [
        "eat",
        "relax",
        "explore",
        "shop",
    ]

    for mood in response["moods"]:
        assert mood["place"] is not None
        assert mood["place"]["id"]
        assert mood["place"]["discovery_query"]

    for section in response["sections"]:
        assert len(section["places"]) == 4

        for place in section["places"]:
            assert place["id"]
            assert place["name"]
            assert place["discovery_query"]
