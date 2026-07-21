from dataclasses import dataclass, field


@dataclass(frozen=True)
class SearchIntent:
    original_query: str
    search_query: str
    category: str | None = None
    cuisine: str | None = None
    price_levels: tuple[str, ...] = field(default_factory=tuple)
    preferences: tuple[str, ...] = field(default_factory=tuple)
    max_distance_meters: int | None = None
    open_now: bool | None = None
