"""v2 application package.

This package intentionally wraps the legacy ``app.py`` module. That preserves
local usage while giving Vercel a package-style entrypoint where v2 security and
routes can be installed incrementally.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def _load_legacy_module():
    base_dir = Path(__file__).resolve().parents[1]
    legacy_path = base_dir / "app.py"
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))

    spec = importlib.util.spec_from_file_location("_cantina_legacy_app", legacy_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Não foi possível carregar {legacy_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("_cantina_legacy_app", module)
    spec.loader.exec_module(module)
    return module


_legacy = _load_legacy_module()
app = _legacy.app


def create_app():
    if not getattr(app, "_v2_installed", False):
        from .routes import register_v2_blueprints
        from .security import install_security_hooks

        register_v2_blueprints(app)
        install_security_hooks(app)
        app._v2_installed = True
    return app


create_app()
