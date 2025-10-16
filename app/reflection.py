"""
Daily reflection entry-point executed by systemd.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from personality import PERSONA, make_reflection_entry
from senses import capture_snapshot


def _log_path() -> Path:
    base = os.getenv("AILA_LOG_DIR", "/var/log")
    return Path(base) / "aila-reflection.log"


def main() -> None:
    snapshot = capture_snapshot()
    summary = snapshot.summary()
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "persona": PERSONA.name,
        "summary": make_reflection_entry(summary, None),
        "metrics": snapshot.as_dict(),
    }

    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True) + "\n")


if __name__ == "__main__":
    main()
