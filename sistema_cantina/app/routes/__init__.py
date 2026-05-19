"""Blueprint registration for the v2 layer."""

from __future__ import annotations


def register_v2_blueprints(app):
    from .auth import bp as auth_bp

    app.register_blueprint(auth_bp)
