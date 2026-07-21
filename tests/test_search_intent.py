from app.models.search_intent import SearchIntent


def test_search_intent_stores_structured_search_preferences():
    intent = SearchIntent(
        original_query=(
            "Find affordable African food nearby"
        ),
        search_query="African restaurant",
        category="restaurant",
        cuisine="African",
        price_levels=("PRICE_LEVEL_INEXPENSIVE",),
        preferences=("affordable",),
        max_distance_meters=1600,
        open_now=True,
    )

    assert intent.original_query == (
        "Find affordable African food nearby"
    )
    assert intent.search_query == "African restaurant"
    assert intent.category == "restaurant"
    assert intent.cuisine == "African"
    assert intent.price_levels == (
        "PRICE_LEVEL_INEXPENSIVE",
    )
    assert intent.preferences == ("affordable",)
    assert intent.max_distance_meters == 1600
    assert intent.open_now is True


def test_search_intent_uses_safe_empty_defaults():
    intent = SearchIntent(
        original_query="coffee",
        search_query="coffee",
    )

    assert intent.category is None
    assert intent.cuisine is None
    assert intent.price_levels == ()
    assert intent.preferences == ()
    assert intent.max_distance_meters is None
    assert intent.open_now is None


def test_search_intent_is_immutable():
    intent = SearchIntent(
        original_query="coffee",
        search_query="coffee",
    )

    try:
        intent.search_query = "tea"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "SearchIntent should be immutable"
        )
