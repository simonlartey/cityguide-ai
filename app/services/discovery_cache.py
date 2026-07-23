from dataclasses import dataclass
from threading import Lock
from time import monotonic
from typing import Any


@dataclass(frozen=True)
class CachedDiscovery:
    expires_at: float
    payload: dict[str, Any]


class DiscoveryCache:
    def __init__(
        self,
        ttl_seconds: int = 21_600,
    ) -> None:
        self.ttl_seconds = ttl_seconds
        self._entries: dict[
            str,
            CachedDiscovery,
        ] = {}
        self._lock = Lock()

    def get(
        self,
        key: str,
    ) -> dict[str, Any] | None:
        now = monotonic()

        with self._lock:
            cached = self._entries.get(key)

            if cached is None:
                return None

            if cached.expires_at <= now:
                del self._entries[key]
                return None

            return cached.payload

    def set(
        self,
        key: str,
        payload: dict[str, Any],
    ) -> None:
        with self._lock:
            self._entries[key] = CachedDiscovery(
                expires_at=(
                    monotonic() +
                    self.ttl_seconds
                ),
                payload=payload,
            )

    @staticmethod
    def build_key(
        latitude: float,
        longitude: float,
    ) -> str:
        return (
            f"{latitude:.3f}:"
            f"{longitude:.3f}"
        )
