"""Supabase client factory used by the v2 cloud layer.

The import is optional so the legacy local app keeps running even before the
new cloud dependencies are installed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL


class SupabaseUnavailable(RuntimeError):
    """Raised when Supabase credentials or the Python client are unavailable."""


@dataclass(frozen=True)
class SupabaseStatus:
    configured: bool
    package_available: bool
    service_role_available: bool


def _load_create_client():
    try:
        from supabase import create_client  # type: ignore

        return create_client
    except Exception:
        return None


def status() -> SupabaseStatus:
    return SupabaseStatus(
        configured=bool(SUPABASE_URL and SUPABASE_ANON_KEY),
        package_available=_load_create_client() is not None,
        service_role_available=bool(SUPABASE_SERVICE_ROLE_KEY),
    )


def get_supabase_client(use_service_role: bool = False) -> Any:
    create_client = _load_create_client()
    if create_client is None:
        raise SupabaseUnavailable(
            "Pacote 'supabase' não instalado. Execute pip install -r requirements.txt."
        )

    key = SUPABASE_SERVICE_ROLE_KEY if use_service_role else SUPABASE_ANON_KEY
    if not SUPABASE_URL or not key:
        raise SupabaseUnavailable("Variáveis SUPABASE_URL/SUPABASE_*_KEY não configuradas.")

    return create_client(SUPABASE_URL, key)


def get_supabase_admin() -> Any:
    return get_supabase_client(use_service_role=True)
