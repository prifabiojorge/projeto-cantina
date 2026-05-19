from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..security import sign_in, sign_out

bp = Blueprint("v2_auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        ok, message = sign_in(email, password)
        flash(message, "success" if ok else "danger")
        if ok:
            return redirect(request.args.get("next") or url_for("dashboard"))
    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    sign_out()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("v2_auth.login"))
