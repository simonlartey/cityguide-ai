from typing import Any

from app.providers.places.base import PlacesProvider


MOCK_PLACES: list[dict[str, Any]] = [
    {
        "id": "portland-fade-studio",
        "name": "Portland Fade Studio",
        "category": "Barber shop",
        "address": "123 Congress St, Portland, ME 04101",
        "latitude": 43.6591,
        "longitude": -70.2568,
        "rating": 4.9,
        "review_count": 527,
        "distance_miles": 0.4,
        "price_level": 2,
        "open_now": True,
        "hours_text": "Open today: 9:00 AM – 7:00 PM",
        "description": (
            "A highly rated barber studio specializing in textured hair, "
            "fades, curls, and modern styles."
        ),
        "tags": [
            "Textured hair",
            "Highly rated",
            "Walking distance",
        ],
        "match_reasons": [
            "Specializes in textured hair and modern fades",
            "Highly rated by customers",
            "Matches an affordable price range",
            "Close to your location",
        ],
    },
    {
        "id": "crown-and-co",
        "name": "Crown & Co. Barbershop",
        "category": "Barber shop",
        "address": "75 Middle St, Portland, ME 04101",
        "latitude": 43.6577,
        "longitude": -70.2523,
        "rating": 4.8,
        "review_count": 319,
        "distance_miles": 0.7,
        "price_level": 2,
        "open_now": True,
        "hours_text": "Open today: 10:00 AM – 8:00 PM",
        "description": (
            "A downtown barbershop experienced with curls, coils, "
            "textured styles, and student-friendly services."
        ),
        "tags": [
            "Curls and coils",
            "Student-friendly",
            "Open late",
        ],
        "match_reasons": [
            "Experienced with curls, coils, and textured styles",
            "Offers student-friendly pricing",
            "Strong customer-service ratings",
            "Convenient downtown location",
        ],
    },
    {
        "id": "elevate-cuts",
        "name": "Elevate Cuts",
        "category": "Barber shop",
        "address": "210 Forest Ave, Portland, ME 04101",
        "latitude": 43.6618,
        "longitude": -70.2712,
        "rating": 4.7,
        "review_count": 214,
        "distance_miles": 1.1,
        "price_level": 1,
        "open_now": True,
        "hours_text": "Open today: 8:30 AM – 6:30 PM",
        "description": (
            "A budget-friendly barber offering cuts for curls, "
            "waves, and a variety of textured hairstyles."
        ),
        "tags": [
            "Budget-friendly",
            "Curls and waves",
            "Fast availability",
        ],
        "match_reasons": [
            "Budget-friendly pricing",
            "Experience with curls and waves",
            "Fast appointment availability",
            "A strong option for students",
        ],
    },
]


class MockPlacesProvider(PlacesProvider):
    """Return normalized mock places during search development."""

    def search(
        self,
        query: str,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> list[dict[str, Any]]:
        if not query.strip():
            return []

        return [place.copy() for place in MOCK_PLACES]