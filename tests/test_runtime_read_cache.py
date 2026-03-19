import unittest

from axxon_telegram_vms.client import RuntimeReadCache, callback_cache_scope
from axxon_telegram_vms.client.runtime_cache import (
    ADMIN_UI_SCOPE,
    CAMERA_CATALOG_SCOPE,
    CAMERA_UI_SCOPE,
    DETECTOR_INVENTORY_SCOPE,
    SERVER_INFO_SCOPE,
    SERVER_STATISTICS_SCOPE,
    SERVER_VERSION_SCOPE,
)


class RuntimeReadCacheTests(unittest.TestCase):
    def test_inventory_reads_cache_by_scope_ttl(self):
        now = [100.0]
        cache = RuntimeReadCache(
            ttl_by_scope={
                CAMERA_CATALOG_SCOPE: 10.0,
                DETECTOR_INVENTORY_SCOPE: 10.0,
                CAMERA_UI_SCOPE: 10.0,
                SERVER_INFO_SCOPE: 5.0,
                SERVER_VERSION_SCOPE: 30.0,
                SERVER_STATISTICS_SCOPE: 5.0,
                ADMIN_UI_SCOPE: 15.0,
            },
            clock=lambda: now[0],
        )
        loads: list[str] = []

        def _load():
            loads.append("camera")
            return [{"name": f"Gate-{len(loads)}"}]

        first = cache.load_camera_catalog("conn-a", _load)
        second = cache.load_camera_catalog("conn-a", _load)

        self.assertEqual(first, [{"name": "Gate-1"}])
        self.assertEqual(second, [{"name": "Gate-1"}])
        self.assertEqual(len(loads), 1)

        now[0] = 111.0
        third = cache.load_camera_catalog("conn-a", _load)
        self.assertEqual(third, [{"name": "Gate-2"}])
        self.assertEqual(len(loads), 2)

    def test_inventory_invalidation_clears_camera_detector_and_camera_ui_entries(self):
        cache = RuntimeReadCache(clock=lambda: 100.0)
        camera_loads: list[str] = []
        detector_loads: list[str] = []
        ui_loads: list[str] = []

        cache.load_camera_catalog("conn-a", lambda: camera_loads.append("camera") or [{"name": "Gate"}])
        cache.load_detector_inventory("conn-a", lambda: detector_loads.append("detector") or [{"name": "Line"}])
        cache.load_ui_payload("cam:list:0", "ui-a", lambda: ui_loads.append("ui") or {"text": "Cameras"})

        cache.invalidate_inventory()

        cache.load_camera_catalog("conn-a", lambda: camera_loads.append("camera") or [{"name": "Gate"}])
        cache.load_detector_inventory("conn-a", lambda: detector_loads.append("detector") or [{"name": "Line"}])
        cache.load_ui_payload("cam:list:0", "ui-a", lambda: ui_loads.append("ui") or {"text": "Cameras"})

        self.assertEqual(camera_loads, ["camera", "camera"])
        self.assertEqual(detector_loads, ["detector", "detector"])
        self.assertEqual(ui_loads, ["ui", "ui"])

    def test_server_invalidation_keeps_inventory_entries(self):
        cache = RuntimeReadCache(clock=lambda: 100.0)
        loads = {"camera": 0, "server": 0, "version": 0, "stats": 0, "admin": 0}

        def _load_camera():
            loads["camera"] += 1
            return [{"name": f"Gate-{loads['camera']}"}]

        def _load_server():
            loads["server"] += 1
            return {"text": "Overview"}

        def _load_version():
            loads["version"] += 1
            return {"text": "Version"}

        def _load_stats():
            loads["stats"] += 1
            return {"text": "Stats"}

        def _load_admin():
            loads["admin"] += 1
            return {"text": "Admin"}

        cache.load_camera_catalog("conn-a", _load_camera)
        cache.load_ui_payload("srv:menu", "srv-menu", _load_server)
        cache.load_ui_payload("srv:version", "srv-version", _load_version)
        cache.load_ui_payload("srv:stats", "srv-stats", _load_stats)
        cache.load_ui_payload("adm:menu", "adm-menu", _load_admin)

        cache.invalidate_server_info()

        cache.load_camera_catalog("conn-a", _load_camera)
        cache.load_ui_payload("srv:menu", "srv-menu", _load_server)
        cache.load_ui_payload("srv:version", "srv-version", _load_version)
        cache.load_ui_payload("srv:stats", "srv-stats", _load_stats)
        cache.load_ui_payload("adm:menu", "adm-menu", _load_admin)

        self.assertEqual(loads["camera"], 1)
        self.assertEqual(loads["server"], 2)
        self.assertEqual(loads["version"], 2)
        self.assertEqual(loads["stats"], 2)
        self.assertEqual(loads["admin"], 2)

    def test_cached_values_are_returned_as_copies(self):
        cache = RuntimeReadCache(clock=lambda: 100.0)
        first = cache.load_detector_inventory("conn-a", lambda: [{"name": "Vehicle"}])
        first[0]["name"] = "Mutated"

        second = cache.load_detector_inventory("conn-a", lambda: [{"name": "Wrong"}])
        self.assertEqual(second, [{"name": "Vehicle"}])

    def test_uncacheable_callbacks_pass_through_every_time(self):
        cache = RuntimeReadCache(clock=lambda: 100.0)
        loads: list[str] = []

        first = cache.load_ui_payload("cam:inc:0:0", "cam-inc", lambda: loads.append("x") or {"text": "Incidents"})
        second = cache.load_ui_payload("cam:inc:0:0", "cam-inc", lambda: loads.append("x") or {"text": "Incidents"})

        self.assertEqual(first, {"text": "Incidents"})
        self.assertEqual(second, {"text": "Incidents"})
        self.assertEqual(loads, ["x", "x"])

    def test_callback_cache_scope_is_conservative(self):
        self.assertEqual(callback_cache_scope("cam:list:0"), CAMERA_UI_SCOPE)
        self.assertEqual(callback_cache_scope("cam:open:1"), CAMERA_UI_SCOPE)
        self.assertEqual(callback_cache_scope("cam:stream:1"), CAMERA_UI_SCOPE)
        self.assertEqual(callback_cache_scope("srv:menu"), SERVER_INFO_SCOPE)
        self.assertEqual(callback_cache_scope("srv:domain"), SERVER_INFO_SCOPE)
        self.assertEqual(callback_cache_scope("srv:version"), SERVER_VERSION_SCOPE)
        self.assertEqual(callback_cache_scope("srv:stats"), SERVER_STATISTICS_SCOPE)
        self.assertEqual(callback_cache_scope("adm:menu"), ADMIN_UI_SCOPE)
        self.assertEqual(callback_cache_scope("adm:access"), ADMIN_UI_SCOPE)
        self.assertIsNone(callback_cache_scope("cam:inc:1:0"))
        self.assertIsNone(callback_cache_scope("cam:lsnap:1"))
        self.assertIsNone(callback_cache_scope("ev:feed:0"))


if __name__ == "__main__":
    unittest.main()
