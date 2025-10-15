# 🏗️ Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │ MapHeatmap  │  │ WhatIfPanel │  │ ExplanationPanel │   │
│  │  (deck.gl)  │  │  (sliders)  │  │  (SHAP, PDP/ICE) │   │
│  └─────────────┘  └─────────────┘  └──────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │     Zustand State (panelA/B/C, linked mode)          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↕ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────────┐    │
│  │   Risk   │  │  Explain  │  │  Counterfactual       │    │
│  │ Endpoint │  │ Endpoint  │  │     Endpoint          │    │
│  └──────────┘  └───────────┘  └──────────────────────┘    │
│  ┌──────────┐  ┌───────────┐                               │
│  │  Frames  │  │  Spread   │                               │
│  │ Endpoint │  │ Endpoint  │                               │
│  └──────────┘  └───────────┘                               │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                 Service Layer                         │  │
│  │  • RiskService (model inference + calibration)       │  │
│  │  • ExplainService (SHAP, PDP, interactions)          │  │
│  │  • CounterfactualService (surrogate + full rescore)  │  │
│  │  • SpreadService (wind-driven simulation)            │  │
│  │  • FramesService (FDCF fetcher)                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Model Registry                           │  │
│  │  • Booster (LightGBM/XGBoost)                        │  │
│  │  • Calibration map (Isotonic per region)             │  │
│  │  • Training ranges (OOD detection)                   │  │
│  │  • Surrogate model (fast GLM)                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer (DuckDB)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      Parquet Feature Tiles (0.25° daily)             │  │
│  │  • date, lat, lon (keys)                             │  │
│  │  • wind, rh, rain, t2m, vpd (weather)                │  │
│  │  • ignition (label)                                  │  │
│  │  • dqf_mask, data_availability (quality)             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────┐
│                        ETL Pipeline                          │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐ │
│  │   FDCF   │→ │  Weather  │→ │  Labeler │→ │ Features │ │
│  │ Ingest   │  │  Ingest   │  │          │  │  Build   │ │
│  └──────────┘  └───────────┘  └──────────┘  └──────────┘ │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Quality Control                          │  │
│  │  • DQF gating                                        │  │
│  │  • Availability masks                                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       ML Pipeline                            │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Train   │→ │ Calibrate │→ │ Evaluate │→ │  Bundle  │ │
│  │   GBM    │  │ (Isotonic)│  │ (AUC-PR) │  │          │ │
│  └──────────┘  └───────────┘  └──────────┘  └──────────┘ │
│  ┌──────────┐  ┌───────────┐                               │
│  │   SHAP   │  │ Surrogate │                               │
│  │  Report  │  │  Training │                               │
│  └──────────┘  └───────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Training Phase
```
Raw Data (FDCF + ERA5)
    ↓
ETL Pipeline (ingest → label → features → quality)
    ↓
Parquet Tiles (0.25° grid, daily)
    ↓
ML Pipeline (train → calibrate → evaluate → bundle)
    ↓
Model Bundle (booster + calibration + ranges + surrogate)
```

### 2. Inference Phase
```
User Request (lat, lon, date, bbox)
    ↓
FastAPI Endpoint
    ↓
Service Layer (load features from DuckDB)
    ↓
Model Registry (predict + calibrate)
    ↓
Response (probability + CI + explanation)
```

### 3. What-If Phase
```
User Modifies (wind_speed, rh, rain)
    ↓
CounterfactualService
    ├─→ Fast Path: Surrogate GLM (4 features)
    └─→ Full Path: Complete model re-score
    ↓
Delta Analysis (contribution attribution)
    ↓
Response (new probability + delta + reason codes)
```

## Key Design Patterns

### Backend
- **Dependency Injection**: `get_settings()`, `get_model_registry()`
- **Service Layer**: Business logic separated from routes
- **Registry Pattern**: Centralized model management
- **Schema Validation**: Pydantic for all I/O

### Frontend
- **State Management**: Zustand for global state
- **Custom Hooks**: Data fetching abstraction
- **Component Composition**: Reusable UI components
- **API Client**: Centralized fetch with retry logic

### ETL
- **Pipeline Pattern**: Sequential transformations
- **Quality Gates**: DQF filtering at each stage
- **Schema Contracts**: Explicit column definitions

### ML
- **Model Bundling**: All artifacts packaged together
- **Calibration**: Per-region reliability correction
- **Explainability**: SHAP + PDP/ICE built-in
- **Surrogate**: Fast approximation for UX

## Scalability Considerations

### Current (Dev)
- Single-node FastAPI
- In-memory DuckDB
- Synthetic data stubs

### Production Path
- **API**: Multiple uvicorn workers → K8s pods → ALB
- **Storage**: DuckDB → S3 Parquet → Athena/Redshift
- **Caching**: Redis for frequent queries
- **ML**: Model versioning (MLflow) + A/B testing
- **Frontend**: CDN (CloudFront) + API Gateway

## File Organization

```
backend/
  app/
    api/         # HTTP layer (routes)
    services/    # Business logic
    models/      # Data models + registry
    utils/       # Helpers (tiles, ranges, DuckDB)
    core/        # Config + logging

etl/
  *.py          # Data ingestion scripts
  config.yaml   # Pipeline configuration

ml/
  *.py          # Training scripts
  data_contract.md

frontend/
  src/
    api/        # HTTP client + types
    components/ # React components
    hooks/      # Data fetching
    state/      # Zustand store
    pages/      # App entry point

infra/
  docker-compose.yml
  pre-commit-config.yaml
  github/workflows/ci.yml
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Backend | FastAPI | REST API framework |
| ML | LightGBM/XGBoost | Gradient boosting |
| Calibration | Scikit-learn | Isotonic regression |
| Explainability | SHAP | Feature importance |
| Storage | DuckDB + Parquet | Analytics DB |
| ETL | Pandas + Polars | Data transformation |
| Frontend | React + TypeScript | UI framework |
| State | Zustand | State management |
| Viz | deck.gl + ECharts | WebGL + charts |
| Build | Vite | Fast dev server |
| Container | Docker | Containerization |
| CI/CD | GitHub Actions | Automation |

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/risk` | GET | Grid risk assessment |
| `/explain` | GET | Local SHAP explanation |
| `/risk/counterfactual` | POST | What-if analysis |
| `/frames` | GET | FDCF frame URIs |
| `/spread/run` | POST | Fire spread simulation |

## Model Features

### Input Features (14)
- `wind_speed_10m`, `wind_dir_sin`, `wind_dir_cos`
- `gust_10m`, `t2m`, `dewpoint`, `rh`, `vpd`
- `rain_24h`, `rain_72h`
- `recent_fires_72h_20km`
- `month`, `clim_mean`, `clim_amp`

### Monotone Constraints
- `wind_speed_10m: +1` (↑ wind = ↑ risk)
- `rh: -1` (↑ humidity = ↓ risk)
- `rain_24h: -1` (↑ rain = ↓ risk)
- `rain_72h: -1` (↑ cumulative rain = ↓ risk)

### Output
- **Probability**: Fire risk [0, 1]
- **CI**: Confidence interval [lower, upper]
- **Calibration**: Per-region reliability
- **OOD Flag**: Out-of-distribution warning
