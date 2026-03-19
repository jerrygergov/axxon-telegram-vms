"""Environment-backed config loading for the staged client lane."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_str(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _env_int(name: str, default: int) -> int:
    raw = _env_str(name, str(default))
    try:
        return int(raw)
    except ValueError:
        return default


def _env_bool(name: str, default: bool = False) -> bool:
    raw = _env_str(name, "1" if default else "0").lower()
    return raw in {"1", "true", "yes", "on", "y"}


def parse_ids(name: str) -> list[int]:
    raw = _env_str(name)
    if not raw:
        return []
    out: list[int] = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            out.append(int(token))
        except ValueError:
            continue
    return out


def parse_csv_text(name: str) -> list[str]:
    raw = _env_str(name)
    if not raw:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for token in raw.split(","):
        text = token.strip()
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
    return out


@dataclass(frozen=True)
class AxxonConfig:
    host: str
    user: str
    password: str
    port: int
    log_file: str

    @property
    def as_cli(self) -> list[str]:
        return [
            "--host",
            self.host,
            "--user",
            self.user,
            "--password",
            self.password,
            "--port",
            str(self.port),
        ]


@dataclass(frozen=True)
class TelegramBotConfig:
    token: str
    authorized_users: list[int]
    admin_users: list[int]
    send_rate_limit_count: int
    send_rate_limit_period_sec: int
    duplicate_window_sec: int
    enable_daily_counters: bool
    max_subscriptions_per_user: int
    max_events_per_day: int
    min_notification_interval_sec: int
    subscription_poll_interval_sec: int
    subscription_poll_window_sec: int
    subscription_poll_limit: int
    subscription_attach_media: bool
    subscription_use_notifier: bool
    subscription_notifier_timeout_sec: int
    subscription_fallback_polling: bool
    live_in_chat_interval_sec: int
    live_in_chat_max_duration_sec: int
    live_overlay: bool
    macro_execution_enabled: bool
    macro_allowed_ids: list[str]
    macro_allowed_names: list[str]
    macro_confirm_ttl_sec: int
    ptz_control_enabled: bool
    ptz_allowed_camera_aps: list[str]
    ptz_allowed_camera_names: list[str]
    ptz_confirm_ttl_sec: int


@dataclass(frozen=True)
class SecureProfileConfig:
    enabled: bool
    master_key: str
    storage_dir: str
    profile_name: str


def load_axxon_config() -> AxxonConfig:
    return AxxonConfig(
        host=_env_str("AXXON_HOST"),
        user=_env_str("AXXON_USER", "root"),
        password=_env_str("AXXON_PASS"),
        port=_env_int("AXXON_PORT", 80),
        log_file=_env_str("AXXON_LOG_FILE", "/tmp/axxon_web_api.log"),
    )


def load_tg_bot_config() -> TelegramBotConfig:
    return TelegramBotConfig(
        token=_env_str("TG_BOT_TOKEN"),
        authorized_users=parse_ids("AUTHORIZED_USERS"),
        admin_users=parse_ids("ADMIN_USERS"),
        send_rate_limit_count=max(1, _env_int("TG_SEND_RATE_LIMIT_COUNT", 4)),
        send_rate_limit_period_sec=max(1, _env_int("TG_SEND_RATE_LIMIT_PERIOD_SEC", 20)),
        duplicate_window_sec=max(0, _env_int("TG_DUPLICATE_WINDOW_SEC", 30)),
        enable_daily_counters=_env_bool("TG_ENABLE_DAILY_COUNTERS", True),
        max_subscriptions_per_user=max(1, _env_int("TG_MAX_SUBSCRIPTIONS_PER_USER", 5)),
        max_events_per_day=max(1, _env_int("TG_MAX_EVENTS_PER_DAY", 100)),
        min_notification_interval_sec=max(0, _env_int("TG_MIN_NOTIFICATION_INTERVAL_SEC", 5)),
        subscription_poll_interval_sec=max(1, _env_int("TG_SUBSCRIPTION_POLL_INTERVAL_SEC", 8)),
        subscription_poll_window_sec=max(30, _env_int("TG_SUBSCRIPTION_POLL_WINDOW_SEC", 1800)),
        subscription_poll_limit=max(1, _env_int("TG_SUBSCRIPTION_POLL_LIMIT", 50)),
        subscription_attach_media=_env_bool("TG_SUBSCRIPTION_ATTACH_MEDIA", True),
        subscription_use_notifier=_env_bool("TG_SUBSCRIPTION_USE_NOTIFIER", True),
        subscription_notifier_timeout_sec=max(1, _env_int("TG_SUBSCRIPTION_NOTIFIER_TIMEOUT_SEC", 25)),
        subscription_fallback_polling=_env_bool("TG_SUBSCRIPTION_FALLBACK_POLLING", False),
        live_in_chat_interval_sec=max(1, _env_int("TG_LIVE_IN_CHAT_INTERVAL_SEC", 3)),
        live_in_chat_max_duration_sec=max(30, _env_int("TG_LIVE_IN_CHAT_MAX_DURATION_SEC", 90)),
        live_overlay=_env_bool("TG_LIVE_OVERLAY", True),
        macro_execution_enabled=_env_bool("TG_MACRO_EXECUTION_ENABLED", False),
        macro_allowed_ids=parse_csv_text("TG_MACRO_ALLOWED_IDS"),
        macro_allowed_names=parse_csv_text("TG_MACRO_ALLOWED_NAMES"),
        macro_confirm_ttl_sec=max(30, _env_int("TG_MACRO_CONFIRM_TTL_SEC", 300)),
        ptz_control_enabled=_env_bool("TG_PTZ_CONTROL_ENABLED", False),
        ptz_allowed_camera_aps=parse_csv_text("TG_PTZ_ALLOWED_CAMERA_APS"),
        ptz_allowed_camera_names=parse_csv_text("TG_PTZ_ALLOWED_CAMERA_NAMES"),
        ptz_confirm_ttl_sec=max(30, _env_int("TG_PTZ_CONFIRM_TTL_SEC", 300)),
    )


def load_secure_profile_config() -> SecureProfileConfig:
    return SecureProfileConfig(
        enabled=_env_bool("AXXON_SECURE_PROFILE_ENABLED", False),
        master_key=_env_str("AXXON_SECURE_PROFILE_MASTER_KEY"),
        storage_dir=_env_str("AXXON_SECURE_PROFILE_DIR", "/tmp/axxon_secure_profiles"),
        profile_name=_env_str("AXXON_SECURE_PROFILE_NAME", "default"),
    )


__all__ = [
    "AxxonConfig",
    "SecureProfileConfig",
    "TelegramBotConfig",
    "load_axxon_config",
    "load_secure_profile_config",
    "load_tg_bot_config",
    "parse_csv_text",
    "parse_ids",
]
