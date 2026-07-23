from typing import Any

from app.providers.places.base import PlacesProvider
from app.schemas.discovery import DiscoveryRequest

DISCOVERY_MOODS = (
    {
        "id": "eat",
        "query": (
            "popular local restaurants and food "
            "nearby"
        ),
    },
    {
        "id": "relax",
        "query": (
            "relaxing cafes parks and peaceful "
            "places nearby"
        ),
    },
    {
        "id": "explore",
        "query": (
            "interesting attractions activities and "
            "places to explore nearby"
        ),
    },
    {
        "id": "shop",
        "query": (
            "popular local shops boutiques and "
            "markets nearby"
        ),
    },
)

DISCOVERY_SECTIONS = (
    {
        "id": "trending",
        "eyebrow": "Popular around your area",
        "title": "Trending Near You",
        "description": (
            "See what is trending right now."
        ),
        "queries": (
            "popular rooftop restaurants and scenic places",
            "popular cafes and coffee shops",
            "live music and entertainment venues",
        ),
    },
    {
        "id": "students",
        "eyebrow": "Made for campus life",
        "title": "For Students",
        "description": (
            "Useful picks for your budget and lifestyle."
        ),
        "queries": (
            "quiet study spots with Wi-Fi and outlets",
            "highly rated affordable restaurants for students",
            "casual group hangout places for students",
        ),
    },
    {
        "id": "hidden-gems",
        "eyebrow": "Go beyond the obvious",
        "title": "Hidden Gems",
        "description": (
            "Local places worth discovering."
        ),
        "queries": (
            "independent bookstores and unique local shops",
            "international markets and specialty food stores",
            "underrated scenic places and local favorites",
        ),
    },
)


class DiscoveryService:
    def __init__(
        self,
        places_provider: PlacesProvider,
    ) -> None:
        self.places_provider = places_provider

    def discover(
        self,
        request: DiscoveryRequest,
    ) -> dict[str, Any]:
        moods = self._build_moods(
            latitude=request.location.latitude,
            longitude=request.location.longitude,
        )

        sections = [
            self._build_section(
                definition,
                latitude=request.location.latitude,
                longitude=request.location.longitude,
            )
            for definition in DISCOVERY_SECTIONS
        ]

        return {
            "location": {
                "latitude": request.location.latitude,
                "longitude": request.location.longitude,
            },
            "moods": moods,
            "sections": sections,
        }

    def _build_moods(
        self,
        *,
        latitude: float,
        longitude: float,
    ) -> list[dict[str, Any]]:
        moods: list[dict[str, Any]] = []
        selected_ids: set[str] = set()

        for definition in DISCOVERY_MOODS:
            results = self.places_provider.search(
                query=definition["query"],
                latitude=latitude,
                longitude=longitude,
            )

            place = self._select_place(
                results,
                selected_ids,
            )

            if place is None:
                moods.append(
                    {
                        "id": definition["id"],
                        "place": None,
                    }
                )
                continue

            normalized_place = place.copy()
            normalized_place["discovery_query"] = (
                definition["query"]
            )

            moods.append(
                {
                    "id": definition["id"],
                    "place": normalized_place,
                }
            )

            place_id = normalized_place.get("id")

            if isinstance(place_id, str):
                selected_ids.add(place_id)

        return moods

    def _build_section(
        self,
        definition: dict[str, Any],
        *,
        latitude: float,
        longitude: float,
    ) -> dict[str, Any]:
        selected_places: list[dict[str, Any]] = []
        selected_ids: set[str] = set()
        maximum_places = 4

        for query in definition["queries"]:
            results = self.places_provider.search(
                query=query,
                latitude=latitude,
                longitude=longitude,
            )

            for place in results:
                place_id = place.get("id")

                if (
                    not isinstance(place_id, str)
                    or not place_id
                    or place_id in selected_ids
                ):
                    continue

                normalized_place = place.copy()
                normalized_place["discovery_query"] = (
                    query
                )

                selected_places.append(
                    normalized_place
                )
                selected_ids.add(place_id)

                if (
                    len(selected_places)
                    >= maximum_places
                ):
                    break

            if (
                len(selected_places)
                >= maximum_places
            ):
                break

        return {
            "id": definition["id"],
            "eyebrow": definition["eyebrow"],
            "title": definition["title"],
            "description": definition["description"],
            "places": selected_places,
        }

    @staticmethod
    def _select_place(
        places: list[dict[str, Any]],
        selected_ids: set[str],
    ) -> dict[str, Any] | None:
        for place in places:
            place_id = place.get("id")

            if (
                isinstance(place_id, str)
                and place_id
                and place_id not in selected_ids
                and place.get("photos")
            ):
                return place

        for place in places:
            place_id = place.get("id")

            if (
                isinstance(place_id, str)
                and place_id
                and place_id not in selected_ids
            ):
                return place

        return None
