"""Stub surrogate trainer producing coefficients for the counterfactual emulator."""

from __future__ import annotations

from pathlib import Path

from joblib import dump

MODEL_DIR = Path(__file__).resolve().parents[1] / "backend" / "models" / "bundles" / "current"


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    surrogate = {"coefficients": {"wind_speed_10m": 0.01, "rh": -0.002}, "intercept": 0.25}
    output = MODEL_DIR / "surrogate.joblib"
    dump(surrogate, output)
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
