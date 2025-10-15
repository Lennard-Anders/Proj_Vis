# Wildfire Risk – Complete Guide (Windows/PowerShell friendly)

Wildfire Risk is a reproducible monorepo that bundles data engineering, model training, inference APIs, monitoring, and a web UI for synthetic wildfire risk exploration. It supports both an all-in-Docker workflow and a manual local dev setup.

Quick links
- Frontend dev: Node.js + Vite
- Backend dev: Python 3.11 + FastAPI
- Full local stack: Docker Desktop + docker compose + Make
- Tests: pytest (backend), Vitest (frontend)

Contents
- Architecture
- Prerequisites
- Quickstart (Docker)
- Quickstart (Manual)
- Tests & Quality
- Troubleshooting
- Data Contract
- Repository Layout
- CI/CD
- Contributing

## Architecture

- Backend (FastAPI): Risk tiles, explanations, counterfactuals, frames, spread simulations. Loads model bundles and synthetic data tiles.
- Frontend (React + Vite + deck.gl): Tri-view map, what-if controls, and explanation panels.
- ETL (Python batch): Synthetic feature tiles, labels, quality metrics.
- ML (Python): Training, calibration, packaging bundles.
- Edge (Nginx): Proxies `/api` and serves static assets.
- Observability (Prometheus + Grafana): Metrics and dashboards.

Data flows: ETL → Parquet features → ML bundle → Backend inference → Frontend visualization. Counterfactuals use a surrogate for instant UX, with an option to re-score via the full model.

## Prerequisites

Choose one path:

1) All-in Docker (recommended)
- Docker Desktop for Windows + WSL 2 enabled
- Make (optional): `choco install make`

2) Manual dev
- Python 3.11 (add to PATH)
- Node.js LTS (includes npm)
- Git (optional)

## Quickstart – Docker

From repo root (`wildfire-risk/`):

```powershell
make up
```

Local services:
- Frontend: http://localhost:8080
- API gateway: http://localhost:8080/api
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

Stop:

```powershell
docker compose down
```

## Quickstart – Manual Dev

### Backend (FastAPI)

```powershell
# Create & activate venv
python -m venv .venv
. .\.venv\Scripts\Activate.ps1

# Install deps
pip install -r backend/requirements.txt

# Run API (auto-reload)
python -m uvicorn backend.app.main:app --reload --port 8000
```

Open:
- API base: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

### Frontend (React + Vite)

```powershell
cd frontend
npm install
npm run dev
```

Open:
- Frontend: http://localhost:5173
Note: Vite proxies `/api` to the backend as configured in `vite.config.ts`.

### ETL & ML (synthetic)

```powershell
make etl     # Run ETL stubs
make bundle  # Build synthetic model bundle
```

If `make` isn’t available, run the scripts in `etl/` and `ml/` directly.

## Tests & Quality

Backend (pytest):

```powershell
. .\.venv\Scripts\Activate.ps1
pytest -q backend
```

Frontend (Typecheck, Lint, Unit):

```powershell
cd frontend
npm run typecheck
npm run lint
npm test -- --run
```

Note: If VS Code shows errors like “react/jsx-runtime not found”, ensure `npm install` completed successfully.

## Troubleshooting

- npm not found: Install Node.js LTS and restart your terminal.
- Port in use: Change ports (Vite 5173, backend 8000) or stop the conflicting process.
- Docker won’t start: Ensure WSL 2 is enabled and Docker Desktop is running.
- jest-dom typings: Run `npm install` in `frontend`. `tsconfig.json` already includes `@testing-library/jest-dom` types.

## Data Contract

Daily 0.25° grids. See `ml/data_contract.md`. Keys: `date`, `lat`, `lon`.
- Static: `month`, `clim_mean`, `clim_amp`, `region_id`
- Dynamic: wind, humidity, precipitation, recent fire indicators
- Quality: `dqf_mask`, `data_availability`

Bundles in `backend/models/bundles/current/`: booster/calibration metadata, feature order, SHAP background, surrogate. Backend returns synthetic JSON following these API contracts.

## Repository Layout

```
├─ backend/      FastAPI app, services, utils
├─ frontend/     Vite React UI with deck.gl
├─ etl/          Batch ingestion & cron
├─ ml/           Training, calibration, bundling
├─ infra/        Nginx, Prometheus, Grafana, K8s
├─ data/         Synthetic schema & samples
└─ docker-compose.yml  Local stack
```

## CI/CD

GitHub Actions runs:
- Python: black, ruff, mypy, pytest
- Frontend: tsc, eslint, vitest
- Docker images build for backend/frontend; push on `main`
- Deploy step is a placeholder

## Contributing

Install pre-commit hooks:

```powershell
pre-commit install
```

CI runs linting (black, ruff, mypy, eslint, tsc) and tests (pytest, vitest) on every PR.
