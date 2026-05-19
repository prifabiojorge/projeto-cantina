"""Configuration helpers for the v2 cloud layer."""

from __future__ import annotations

import os


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on", "sim"}


SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "").strip()
CRON_SECRET = os.environ.get("CRON_SECRET", "").strip()

IS_VERCEL = bool(os.environ.get("VERCEL"))
V2_AUTH_REQUIRED = _bool_env("V2_AUTH_REQUIRED", default=IS_VERCEL)


def is_supabase_configured(require_service_role: bool = False) -> bool:
    if not SUPABASE_URL or "seu-projeto" in SUPABASE_URL:
        return False
    if not SUPABASE_ANON_KEY or "sua-chave" in SUPABASE_ANON_KEY:
        return False
    if require_service_role and (
        not SUPABASE_SERVICE_ROLE_KEY or "sua-service" in SUPABASE_SERVICE_ROLE_KEY
    ):
        return False
    return True


def required_environment_status() -> dict[str, bool]:
    return {
        "SUPABASE_URL": bool(SUPABASE_URL),
        "SUPABASE_ANON_KEY": bool(SUPABASE_ANON_KEY),
        "SUPABASE_SERVICE_ROLE_KEY": bool(SUPABASE_SERVICE_ROLE_KEY),
        "SUPABASE_JWT_SECRET": bool(SUPABASE_JWT_SECRET),
        "CRON_SECRET": bool(CRON_SECRET),
    }
