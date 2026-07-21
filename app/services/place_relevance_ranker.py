import re
from collections.abc import Iterable


class PlaceRelevanceRanker:
    """Rank places by how closely their metadata matches a search query."""

    GENERIC_QUERY_TERMS = {
        "a",
        "an",
        "and",
        "at",
        "for",
        "in",
        "me",
        "near",
        "nearby",
        "of",
        "place",
        "places",
        "the",
        "to",
        "with",
    }

    QUERY_SYNONYM_GROUPS = (
        {
            "affordable",
            "budget",
            "cheap",
            "inexpensive",
        },
        {
            "barber",
            "barbershop",
            "fade",
            "hair",
        },
        {
            "cafe",
            "coffee",
            "coffeehouse",
        },
        {
            "grocery",
            "groceries",
            "market",
            "supermarket",
        },
        {
            "peaceful",
            "quiet",
            "study",
            "workspace",
        },
        {
            "dining",
            "food",
            "restaurant",
        },
    )

    def rank(
        self,
        query: str,
        places: Iterable[dict],
    ) -> list[dict]:
        """Return places ordered from most to least relevant."""

        query_terms = self._query_terms(query)

        return sorted(
            places,
            key=lambda place: self._sort_key(
                place,
                query_terms,
            ),
        )

    def score(
        self,
        query: str,
        place: dict,
    ) -> int:
        """Calculate a deterministic relevance score for one place."""

        query_terms = self._query_terms(query)

        if not query_terms:
            return 0

        name_terms = self._tokenize(place.get("name"))
        category_terms = self._tokenize(
            place.get("category")
        )
        primary_type_terms = self._tokenize(
            place.get("primary_type")
        )
        type_terms = self._tokenize_many(
            place.get("types")
        )

        score = 0
        score += 6 * len(query_terms & primary_type_terms)
        score += 5 * len(query_terms & category_terms)
        score += 4 * len(query_terms & type_terms)
        score += 2 * len(query_terms & name_terms)

        return score

    def _sort_key(
        self,
        place: dict,
        query_terms: set[str],
    ) -> tuple:
        relevance_score = self._score_terms(
            query_terms,
            place,
        )
        rating = self._number_or_zero(
            place.get("rating")
        )
        review_count = self._number_or_zero(
            place.get("review_count")
        )
        distance = self._distance_or_infinity(
            place.get("distance_miles")
        )

        return (
            -relevance_score,
            -rating,
            -review_count,
            distance,
            str(place.get("name", "")).lower(),
        )

    def _score_terms(
        self,
        query_terms: set[str],
        place: dict,
    ) -> int:
        if not query_terms:
            return 0

        name_terms = self._tokenize(place.get("name"))
        category_terms = self._tokenize(
            place.get("category")
        )
        primary_type_terms = self._tokenize(
            place.get("primary_type")
        )
        type_terms = self._tokenize_many(
            place.get("types")
        )

        return (
            6 * len(query_terms & primary_type_terms)
            + 5 * len(query_terms & category_terms)
            + 4 * len(query_terms & type_terms)
            + 2 * len(query_terms & name_terms)
        )

    def _tokenize_many(self, values: object) -> set[str]:
        if not isinstance(values, list):
            return set()

        terms: set[str] = set()

        for value in values:
            terms.update(self._tokenize(value))

        return terms

    def _query_terms(self, query: object) -> set[str]:
        terms = self._tokenize(query)
        expanded_terms = set(terms)

        for synonym_group in self.QUERY_SYNONYM_GROUPS:
            if terms & synonym_group:
                expanded_terms.update(synonym_group)

        return expanded_terms

    def _tokenize(self, value: object) -> set[str]:
        if not isinstance(value, str):
            return set()

        normalized = value.lower().replace("_", " ")
        terms = set(
            re.findall(r"[a-z0-9]+", normalized)
        )

        return terms - self.GENERIC_QUERY_TERMS

    @staticmethod
    def _number_or_zero(value: object) -> float:
        if isinstance(value, bool):
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        return 0.0

    @staticmethod
    def _distance_or_infinity(value: object) -> float:
        if isinstance(value, bool):
            return float("inf")

        if isinstance(value, (int, float)):
            return float(value)

        return float("inf")
