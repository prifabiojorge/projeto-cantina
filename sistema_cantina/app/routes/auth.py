from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..security import sign_in, sign_out, current_role

bp = Blueprint("v2_auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        ok, message = sign_in(email, password)
        flash(message, "success" if ok else "danger")
        if ok:
            destino = request.args.get('next', '')
            if not destino.startswith('/') or destino.startswith('//') or '\\' in destino:
                destino = {'portaria':'/portaria', 'cantina':'/cantina'}.get(current_role(), '/dashboard')
            return redirect(destino)
    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    sign_out()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("v2_auth.login"))
