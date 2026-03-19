"""Conservative read-cache helpers for the scripts-owned runtime."""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
import json
from typing import Any

from .cache import TTLCache

CAMERA_CATALOG_SCOPE = "camera_catalog"
DETECTOR_INVENTORY_SCOPE = "detector_inventory"
CAMERA_UI_SCOPE = "camera_ui"
SERVER_INFO_SCOPE = "server_info"
SERVER_VERSION_SCOPE = "server_version"
SERVER_STATISTICS_SCOPE = "server_statistics"
ADMIN_UI_SCOPE = "admin_ui"

INVENTORY_SCOPES = (
    CAMERA_CATALOG_SCOPE,
    DETECTOR_INVENTORY_SCOPE,
    CAMERA_UI_SCOPE,
)
SERVER_SCOPES = (
    SERVER_INFO_SCOPE,
    SERVER_VERSION_SCOPE,
    SERVER_STATISTICS_SCOPE,
    ADMIN_UI_SCOPE,
)

DEFAULT_RUNTIME_CACHE_TTLS: dict[str, float] = {
    CAMERA_CATALOG_SCOPE: 15.0,
    DETECTOR_INVENTORY_SCOPE: 15.0,
    CAMERA_UI_SCOPE: 15.0,
    SERVER_INFO_SCOPE: 5.0,
    SERVER_VERSION_SCOPE: 30.0,
    SERVER_STATISTICS_SCOPE: 5.0,
    ADMIN_UI_SCOPE: 15.0,
}

_MISSING = object()


def callback_cache_scope(callback_data: str) -> str | None:
    data = str(callback_data or "").strip()
    if data in {"srv:menu", "srv:domain"}:
        return SERVER_INFO_SCOPE
    if data == "srv:version":
        return SERVER_VERSION_SCOPE
    if data == "srv:stats":
        return SERVER_STATISTICS_SCOPE
    if data.startswith("adm:"):
        return ADMIN_UI_SCOPE
    if data.startswith("cam:list:") or data.startswith("cam:open:") or data.startswith("cam:stream:"):
        return CAMERA_UI_SCOPE
    return None


def build_runtime_cache_key(**parts: object) -> str:
    return json.dumps(parts, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class RuntimeReadCache:
    def __init__(
        self,
        *,
        ttl_by_scope: dict[str, float] | None = None,
        clock: Callable[[], float] | None = None,
    ):
        self._ttl_by_scope = dict(DEFAULT_RUNTIME_CACHE_TTLS)
        if ttl_by_scope:
            self._ttl_by_scope.update({key: float(value) for key, value in ttl_by_scope.items()})
        self._cache = TTLCache[str, Any](
            default_ttl_sec=max(self._ttl_by_scope.values()),
            clock=clock,
        )
        self._keys_by_scope: dict[str, set[str]] = {}

    def load_camera_catalog(self, cache_key: str, loader: Callable[[], Any]) -> Any:
        return self._load(CAMERA_CATALOG_SCOPE, cache_key, loader)

    def load_detector_inventory(self, cache_key: str, loader: Callable[[], Any]) -> Any:
        return self._load(DETECTOR_INVENTORY_SCOPE, cache_key, loader)

    def load_ui_payload(self, callback_data: str, cache_key: str, loader: Callable[[], Any]) -> Any:
        scope = callback_cache_scope(callback_data)
        if not scope:
            return loader()
        return self._load(scope, cache_key, loader)

    def invalidate_inventory(self) -> None:
        self._invalidate_scopes(INVENTORY_SCOPES)

    def invalidate_server_info(self) -> None:
        self._invalidate_scopes(SERVER_SCOPES)

    def invalidate_all(self) -> None:
        self._cache.clear()
        self._keys_by_scope.clear()

    def ttl_for(self, scope: str) -> float:
        try:
            return self._ttl_by_scope[scope]
        except KeyError as ex:
            raise KeyError(f"unknown runtime cache scope: {scope}") from ex

    def _load(self, scope: str, cache_key: str, loader: Callable[[], Any]) -> Any:
        entry_key = self._entry_key(scope, cache_key)
        self._keys_by_scope.setdefault(scope, set()).add(entry_key)

        cached = self._cache.get(entry_key, _MISSING)
        if cached is not _MISSING:
            return deepcopy(cached)

        loaded = deepcopy(loader())
        self._cache.set(entry_key, loaded, ttl_sec=self.ttl_for(scope))
        return deepcopy(loaded)

    def _invalidate_scopes(self, scopes: tuple[str, ...]) -> None:
        for scope in scopes:
            keys = tuple(self._keys_by_scope.pop(scope, ()))
            for entry_key in keys:
                self._cache.invalidate(entry_key)

    @staticmethod
    def _entry_key(scope: str, cache_key: str) -> str:
        return f"{scope}:{cache_key}"


__all__ = [
    "CAMERA_CATALOG_SCOPE",
    "CAMERA_UI_SCOPE",
    "ADMIN_UI_SCOPE",
    "DEFAULT_RUNTIME_CACHE_TTLS",
    "DETECTOR_INVENTORY_SCOPE",
    "INVENTORY_SCOPES",
    "RuntimeReadCache",
    "SERVER_INFO_SCOPE",
    "SERVER_SCOPES",
    "SERVER_STATISTICS_SCOPE",
    "SERVER_VERSION_SCOPE",
    "build_runtime_cache_key",
    "callback_cache_scope",
]
