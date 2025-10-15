# Wildfire Risk Monorepo

Wildfire Risk is a reproducible monorepo that bundles data engineering, model training, inference APIs, monitoring, and UI tooling for synthetic wildfire risk exploration. The stack is designed for local development with Docker and a path to Kubernetes deployment.

## Architecture

- **Backend (FastAPI)**: Serves risk tiles, local explanations, counterfactual reasoning, frames, and spread simulations. Loads model bundles and synthetic data tiles.
- **Frontend (React + Vite + deck.gl)**: Provides a tri-view map with what-if controls and explanation panels.
- **ETL (Python batch)**: Builds synthetic feature tiles, labels, and quality metrics.
- **ML (Python training)**: Trains gradient boosted models, calibrates probabilities, and packages bundles.
- **Edge (Nginx)**: Proxies `/api` traffic to the backend and serves the frontend.
- **Observability (Prometheus + Grafana)**: Exposes metrics and dashboards for API health and system overview.

Data flows from ETL → feature Parquet tiles → ML bundle → Backend inference. Counterfactuals use a surrogate emulator for interactive UX, with a full re-score option.

## Quickstart

```bash
# within the repo root
make up
```

Services exposed locally:

- Frontend: http://localhost:8080
- API gateway: http://localhost:8080/api
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin:admin by default)

To work on individual components:

```bash
make serve   # backend (FastAPI + uvicorn reload)
make ui      # frontend (Vite dev server)
make etl     # synthetic ingestion (stub)
make bundle  # package synthetic model bundle
```

## Data Contract

All feature tiles are daily 0.25° grids with schema documented in `ml/data_contract.md`. Keys: `date`, `lat`, `lon`. Static features include `month`, `clim_mean`, `clim_amp`, `region_id`. Dynamic features include wind, humidity, precipitation, and recent fire indicators. Quality fields (`dqf_mask`, `data_availability`) track upstream coverage.

Model bundles live under `backend/models/bundles/current/` and contain booster binaries, calibration metadata, feature order, SHAP background sets, and surrogate emulators. The backend exposes synthetic JSON aligned with the API contracts in this README.

## Repository Layout

```
├─ backend/      FastAPI application with services and utilities
├─ frontend/     Vite-based UI with tri-view deck.gl panels
├─ etl/          Batch ingestion scripts and cron entrypoint
├─ ml/           Training, calibration, XAI, and bundling scripts
├─ infra/        Nginx, Prometheus, Grafana, and K8s manifests
├─ data/         Synthetic schema files and sample tiles
└─ docker-compose.yml  Local stack definition
```

## Licensing & Attribution

This repository is released under the MIT License (see `LICENSE`). Synthetic data assets are provided for demonstration only; replace with authoritative sources for production workloads.

## Diagrams

High-level flow:

```
[ETL cron] -> [feature store (Parquet/DuckDB)] -> [ML bundle builder]
      -> [backend FastAPI] <-/api-> [frontend deck.gl tri-view]
      -> [Prometheus] -> [Grafana dashboards]
```

## Contributing

Install pre-commit hooks via `pre-commit install`. CI linting (black, ruff, mypy, eslint, tsc) and tests (pytest, vitest) run on every pull request.
