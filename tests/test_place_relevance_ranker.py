from app.services.place_relevance_ranker import (
    PlaceRelevanceRanker,
)


def test_ranker_prioritizes_exact_place_type_match():
    ranker = PlaceRelevanceRanker()

    places = [
        {
            "name": "Popular Downtown Grill",
            "category": "Restaurant",
            "primary_type": "restaurant",
            "types": ["restaurant", "food"],
            "rating": 4.9,
            "review_count": 2400,
            "distance_miles": 0.2,
        },
        {
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

    ranked = ranker.rank(
        "African restaurant near me",
        places,
    )

    assert ranked[0]["name"] == "Lagos Kitchen"


def test_ranker_uses_category_and_type_metadata():
    ranker = PlaceRelevanceRanker()

    score = ranker.score(
        "barber shop",
        {
            "name": "Portland Fade Studio",
            "category": "Barber shop",
            "primary_type": "barber_shop",
            "types": [
                "barber_shop",
                "hair_care",
            ],
        },
    )

    assert score > 0


def test_ranker_uses_rating_as_relevance_tiebreaker():
    ranker = PlaceRelevanceRanker()

    places = [
        {
            "name": "Cafe One",
            "category": "Cafe",
            "primary_type": "cafe",
            "types": ["cafe"],
            "rating": 4.2,
            "review_count": 100,
        },
        {
            "name": "Cafe Two",
            "category": "Cafe",
            "primary_type": "cafe",
            "types": ["cafe"],
            "rating": 4.8,
            "review_count": 80,
        },
    ]

    ranked = ranker.rank("cafe", places)

    assert ranked[0]["name"] == "Cafe Two"


def test_ranker_uses_review_count_after_rating():
    ranker = PlaceRelevanceRanker()

    places = [
        {
            "name": "Cafe One",
            "category": "Cafe",
            "primary_type": "cafe",
            "types": ["cafe"],
            "rating": 4.5,
            "review_count": 120,
        },
        {
            "name": "Cafe Two",
            "category": "Cafe",
            "primary_type": "cafe",
            "types": ["cafe"],
            "rating": 4.5,
            "review_count": 600,
        },
    ]

    ranked = ranker.rank("cafe", places)

    assert ranked[0]["name"] == "Cafe Two"


def test_ranker_uses_distance_after_quality_tiebreakers():
    ranker = PlaceRelevanceRanker()

    places = [
        {
            "name": "Far Cafe",
            "category": "Cafe",
            "primary_type": "cafe",
            "types": ["cafe"],
            "rating": 4.5,
            "review_count": 100,
            "distance_miles": 2.0,
        },
        {
            "name": "Near Cafe",
            "category": "Cafe",
            "primary_type": "cafe",
            "types": ["cafe"],
            "rating": 4.5,
            "review_count": 100,
            "distance_miles": 0.4,
        },
    ]

    ranked = ranker.rank("cafe", places)

    assert ranked[0]["name"] == "Near Cafe"


def test_ranker_handles_missing_and_malformed_metadata():
    ranker = PlaceRelevanceRanker()

    places = [
        {
            "name": None,
            "category": None,
            "primary_type": None,
            "types": "restaurant",
            "rating": "unknown",
            "review_count": None,
            "distance_miles": None,
        }
    ]

    ranked = ranker.rank("restaurant", places)

    assert len(ranked) == 1
    assert ranker.score("restaurant", places[0]) == 0


def test_ranker_does_not_mutate_input_order():
    ranker = PlaceRelevanceRanker()

    places = [
        {
            "name": "General Restaurant",
            "category": "Restaurant",
            "primary_type": "restaurant",
            "types": ["restaurant"],
        },
        {
            "name": "African Kitchen",
            "category": "African restaurant",
            "primary_type": "african_restaurant",
            "types": ["african_restaurant"],
        },
    ]

    original_names = [
        place["name"] for place in places
    ]

    ranker.rank("African restaurant", places)

    assert [
        place["name"] for place in places
    ] == original_names


def test_ranker_matches_query_synonyms():
    ranker = PlaceRelevanceRanker()

    places = [
        {
            "name": "Luxury Dining Room",
            "category": "Restaurant",
            "primary_type": "restaurant",
            "types": ["restaurant", "food"],
        },
        {
            "name": "Student Budget Kitchen",
            "category": "Inexpensive restaurant",
            "primary_type": "restaurant",
            "types": [
                "restaurant",
                "food",
                "inexpensive",
            ],
        },
    ]

    ranked = ranker.rank(
        "cheap restaurant",
        places,
    )

    assert ranked[0]["name"] == "Student Budget Kitchen"


def test_ranker_matches_barbershop_variation():
    ranker = PlaceRelevanceRanker()

    places = [
        {
            "name": "General Hair Studio",
            "category": "Hair salon",
            "primary_type": "hair_salon",
            "types": ["hair_care"],
        },
        {
            "name": "Downtown Fade Shop",
            "category": "Barber shop",
            "primary_type": "barber_shop",
            "types": [
                "barber_shop",
                "hair_care",
            ],
        },
    ]

    ranked = ranker.rank(
        "barbershop near me",
        places,
    )

    assert ranked[0]["name"] == "Downtown Fade Shop"


def test_ranker_matches_grocery_word_variations():
    ranker = PlaceRelevanceRanker()

    score = ranker.score(
        "groceries",
        {
            "name": "International Market",
            "category": "Grocery store",
            "primary_type": "grocery_store",
            "types": [
                "grocery_store",
                "market",
            ],
        },
    )

    assert score > 0


def test_synonym_expansion_does_not_mutate_place_metadata():
    ranker = PlaceRelevanceRanker()

    place = {
        "name": "Quiet Corner",
        "category": "Cafe",
        "primary_type": "cafe",
        "types": ["cafe"],
    }
    original_types = list(place["types"])

    ranker.score("study cafe", place)

    assert place["types"] == original_types


def test_ranker_expands_synonyms_from_any_group_term():
    ranker = PlaceRelevanceRanker()

    affordable_score = ranker.score(
        "budget restaurant",
        {
            "name": "Student Kitchen",
            "category": "Inexpensive restaurant",
            "primary_type": "restaurant",
            "types": [
                "restaurant",
                "inexpensive",
            ],
        },
    )

    coffee_score = ranker.score(
        "coffeehouse",
        {
            "name": "Campus Cafe",
            "category": "Cafe",
            "primary_type": "cafe",
            "types": ["cafe"],
        },
    )

    assert affordable_score > 0
    assert coffee_score > 0
