"""Stub training routine that emits a synthetic model artifact."""

from __future__ import annotations

import json
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parents[1] / "backend" / "models" / "bundles" / "current"


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    params = {"model": "gradient_boosting_standalone", "n_trees": 10, "learning_rate": 0.1}
    output = MODEL_DIR / "trained_model.json"
    output.write_text(json.dumps(params, indent=2))
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
