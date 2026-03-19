"""Static foundation registry for the staged architecture passes.

The active runtime still lives under ``scripts/``. This module only records the
intended internal split so later migrations can move incrementally without
changing behavior in the same pass.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ArchitectureLane:
    name: str
    purpose: str
    seed_modules: tuple[str, ...]
    status: str = "placeholder"


ACTIVE_RUNTIME_ENTRYPOINTS: tuple[str, ...] = (
    "scripts/axxon_tg_bot.py",
    "scripts/axxon_tg_ui.py",
    "scripts/axxon_web_api.py",
)


ARCHITECTURE_LANES: tuple[ArchitectureLane, ...] = (
    ArchitectureLane(
        name="client",
        purpose="Raw Axxon transport clients and compatibility adapters.",
        seed_modules=(
            "scripts/axxon_web_api.py",
            "scripts/config_loader.py",
            "scripts/tg_ui_common.py",
            "axxon_telegram_vms/client/config.py",
            "axxon_telegram_vms/client/session.py",
            "axxon_telegram_vms/client/transport.py",
            "axxon_telegram_vms/client/cache.py",
            "axxon_telegram_vms/client/runtime_cache.py",
        ),
        status="seeded",
    ),
    ArchitectureLane(
        name="services",
        purpose="Business orchestration and runtime workflows.",
        seed_modules=(
            "scripts/axxon_tg_bot.py",
            "scripts/live_session_runtime.py",
            "axxon_telegram_vms/services/admin_view.py",
            "axxon_telegram_vms/services/event_search.py",
            "axxon_telegram_vms/services/external_analysis.py",
            "axxon_telegram_vms/services/face_search.py",
            "axxon_telegram_vms/services/license_plate_search.py",
            "axxon_telegram_vms/services/macro_execution.py",
            "axxon_telegram_vms/services/multi_camera_export.py",
            "axxon_telegram_vms/services/ptz_control.py",
            "axxon_telegram_vms/services/subscriptions.py",
        ),
        status="seeded",
    ),
    ArchitectureLane(
        name="models",
        purpose="Normalized domain models and translation helpers.",
        seed_modules=(
            "scripts/camera_catalog.py",
            "scripts/unification_helpers.py",
            "scripts/media_utils.py",
            "axxon_telegram_vms/models/detectors.py",
            "axxon_telegram_vms/models/event_normalization.py",
            "axxon_telegram_vms/models/query_filters.py",
            "axxon_telegram_vms/models/request_envelopes.py",
        ),
        status="seeded",
    ),
    ArchitectureLane(
        name="jobs",
        purpose="Long-running export, search, and notification jobs.",
        seed_modules=(
            "scripts/live_session_runtime.py",
            "axxon_telegram_vms/jobs/external_analysis.py",
            "axxon_telegram_vms/jobs/live_sessions.py",
        ),
        status="seeded",
    ),
    ArchitectureLane(
        name="ui",
        purpose="Telegram-facing formatting, menus, and callback payloads.",
        seed_modules=(
            "scripts/axxon_tg_ui.py",
            "scripts/tg_admin_ui.py",
            "scripts/tg_camera_ui.py",
            "scripts/tg_server_ui.py",
            "scripts/tg_ui_common.py",
        ),
    ),
)
