"""Small pure TTL cache foundation for future client-side inventory caching."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")
_MISSING = object()


@dataclass(frozen=True)
class CacheEntry(Generic[V]):
    value: V
    expires_at: float


class TTLCache(Generic[K, V]):
    def __init__(self, default_ttl_sec: float, clock: Callable[[], float] | None = None):
        ttl = float(default_ttl_sec)
        if ttl <= 0:
            raise ValueError("default_ttl_sec must be greater than zero")
        self._default_ttl_sec = ttl
        self._clock = clock or time.monotonic
        self._entries: dict[K, CacheEntry[V]] = {}

    def get(self, key: K, default: object | None = None) -> V | object | None:
        entry = self._entries.get(key)
        if entry is None:
            return default
        if entry.expires_at <= self._clock():
            self._entries.pop(key, None)
            return default
        return entry.value

    def set(self, key: K, value: V, *, ttl_sec: float | None = None) -> V:
        ttl = self._default_ttl_sec if ttl_sec is None else float(ttl_sec)
        if ttl <= 0:
            raise ValueError("ttl_sec must be greater than zero")
        self._entries[key] = CacheEntry(value=value, expires_at=self._clock() + ttl)
        return value

    def get_or_set(self, key: K, loader: Callable[[], V], *, ttl_sec: float | None = None) -> V:
        value = self.get(key, _MISSING)
        if value is not _MISSING:
            return value
        return self.set(key, loader(), ttl_sec=ttl_sec)

    def invalidate(self, key: K) -> None:
        self._entries.pop(key, None)

    def clear(self) -> None:
        self._entries.clear()

    def __len__(self) -> int:
        self._purge_expired()
        return len(self._entries)

    def _purge_expired(self) -> None:
        now = self._clock()
        expired = [key for key, entry in self._entries.items() if entry.expires_at <= now]
        for key in expired:
            self._entries.pop(key, None)


__all__ = ["CacheEntry", "TTLCache"]
