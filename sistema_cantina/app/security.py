"""Optional Supabase Auth integration for v2 deployments."""

from __future__ import annotations

from functools import wraps
from typing import Callable, Iterable

from flask import abort, flash, redirect, request, session, url_for

from .config import V2_AUTH_REQUIRED
from .supabase_client import SupabaseUnavailable, get_supabase_client

ADMIN_PREFIXES = (
    "/",
    "/dashboard",
    "/api/dashboard",
    "/api/historico",
    "/api/relatorio",
    "/api/whatsapp/teste",
    "/alunos",
    "/admin",
    "/backup",
    "/configuracoes",
    "/relatorio",
    "/relatorios",
)

PUBLIC_PREFIXES = (
    "/health",
    "/login",
    "/logout",
    "/static",
    "/portaria",
    "/cantina",
    "/api/checkin-portaria",
    "/api/checkin-cantina",
    "/api/portaria/contagem-hoje",
    "/api/cantina",
    "/api/cron/relatorio-diario",
)


def current_user() -> dict | None:
    return session.get("v2_user")


def is_authenticated() -> bool:
    return bool(session.get("v2_access_token") and current_user())


def current_role() -> str | None:
    user = current_user() or {}
    return user.get("papel")


def is_admin() -> bool:
    return current_role() == "admin"


def _matches(path: str, prefixes: Iterable[str]) -> bool:
    return any(path == prefix or path.startswith(prefix + "/") for prefix in prefixes)


def requires_admin_auth(path: str) -> bool:
    if not V2_AUTH_REQUIRED:
        return False
    if _matches(path, PUBLIC_PREFIXES):
        return False
    return _matches(path, ADMIN_PREFIXES)


def require_admin(fn: Callable):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            flash("Faça login para acessar a área administrativa.", "warning")
            return redirect(url_for("v2_auth.login", next=request.path))
        if V2_AUTH_REQUIRED and not is_admin():
            abort(403)
        return fn(*args, **kwargs)

    return wrapper


def install_security_hooks(app):
    @app.before_request
    def v2_require_auth_for_admin_routes():
        if not requires_admin_auth(request.path):
            return None
        if not is_authenticated():
            return redirect(url_for("v2_auth.login", next=request.path))
        if not is_admin():
            abort(403)
        return None


def sign_in(email: str, password: str) -> tuple[bool, str]:
    try:
        client = get_supabase_client()
        response = client.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )
    except SupabaseUnavailable as exc:
        return False, str(exc)
    except Exception as exc:
        return False, f"Falha no login Supabase: {exc}"

    session_data = getattr(response, "session", None)
    user_data = getattr(response, "user", None)
    access_token = getattr(session_data, "access_token", None)
    user_id = getattr(user_data, "id", None)
    user_email = getattr(user_data, "email", email)

    if not access_token or not user_id:
        return False, "Supabase não retornou sessão válida."

    papel = ""
    nome = ""
    try:
        perfil_response = (
            client.table("perfis_usuarios")
            .select("papel,nome")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        perfis = getattr(perfil_response, "data", None) or []
        if perfis:
            papel = perfis[0].get("papel") or ""
            nome = perfis[0].get("nome") or ""
    except Exception:
        papel = ""

    if papel != "admin":
        return False, "Usuário autenticado, mas sem perfil administrativo."

    session["v2_access_token"] = access_token
    session["v2_user"] = {"id": user_id, "email": user_email, "papel": papel, "nome": nome}
    session.permanent = True
    return True, "Login realizado com sucesso."


def sign_out() -> None:
    session.pop("v2_access_token", None)
    session.pop("v2_user", None)
