"""Stub evaluation script emitting metric report."""

from __future__ import annotations

import json
from pathlib import Path

REPORT_DIR = Path(__file__).resolve().parents[1] / "data" / "sample"


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    metrics = {
        "pr_auc": 0.72,
        "brier": 0.18,
        "ece": 0.06,
    }
    output = REPORT_DIR / "metrics.json"
    output.write_text(json.dumps(metrics, indent=2))
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
