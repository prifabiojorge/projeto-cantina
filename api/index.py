"""Vercel entrypoint for the Cantina Flask application.

Vercel invokes this module as a Python serverless function. The actual app
still lives in ``sistema_cantina`` so local operators can keep using
``python app.py`` while the v2 cloud deployment imports the same Flask app.
"""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = ROOT_DIR / "sistema_cantina"

for path in (str(ROOT_DIR), str(APP_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

from app import app as application  # noqa: E402

app = application
