from __future__ import annotations

from datetime import datetime
from pathlib import Path


def append_incident(title: str, body: str, memoria_dir: Path | None = None) -> Path:
    base = memoria_dir or Path(__file__).resolve().parents[3] / "memoria"
    target_dir = base / "incidentes"
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + title.lower().replace(" ", "_") + ".md"
    path = target_dir / filename
    path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")
    return path
