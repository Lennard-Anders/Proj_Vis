# 🔥 Multimodal Wildfire Risk Modeling (Americas)

A production-ready monorepo for wildfire risk prediction, explainability, and counterfactual analysis across the Americas. Combines machine learning (LightGBM/XGBoost), multimodal data sources (FDCF, ERA5, climatology), and interactive visualization.

## 🌟 Features

- **Risk Prediction**: 0.25° daily fire probability with confidence intervals
- **Explainability**: SHAP-based local explanations, PDP/ICE, feature interactions
- **Counterfactual "What-If"**: Fast surrogate model for scenario testing
- **Spread Simulation**: Wind-driven fire envelope prototype
- **Calibration**: Per-region Platt/Isotonic calibration for reliability
- **Quality Control**: DQF gating and availability masks
- **Interactive Frontend**: React + TypeScript + deck.gl + ECharts

## 📂 Repository Structure

```
.
├── backend/              # FastAPI + services
│   ├── app/
│   │   ├── api/         # REST endpoints
│   │   ├── services/    # Business logic
│   │   ├── models/      # Pydantic schemas + registry
│   │   └── utils/       # Feature ranges, tiles, DuckDB
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/
│
├── etl/                  # Data ingestion & features
│   ├── ee_fdcf_ingest.py
│   ├── weather_ingest.py
│   ├── labeler.py
│   ├── features_build.py
│   ├── quality.py
│   └── config.yaml
│
├── ml/                   # Training & evaluation
│   ├── train_gbm.py
│   ├── calibrate.py
│   ├── evaluate.py
│   ├── shap_report.py
│   ├── surrogate_train.py
│   ├── bundle.py
│   └── data_contract.md
│
├── frontend/             # React + Vite
│   ├── src/
│   │   ├── api/         # fetch helpers
│   │   ├── components/  # MapHeatmap, WhatIfPanel, etc.
│   │   ├── hooks/       # useRisk, useExplain, useCounterfactual
│   │   ├── state/       # Zustand store
│   │   └── pages/       # App.tsx
│   └── package.json
│
├── infra/
│   ├── docker-compose.yml
│   ├── pre-commit-config.yaml
│   └── github/workflows/ci.yml
│
├── data/
│   ├── schema/
│   └── README.md
│
├── Makefile
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)

### Option 1: Local Development

1. **Install dependencies**:
   ```bash
   make install
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run ETL (optional, uses stub data by default)**:
   ```bash
   make etl
   ```

4. **Train model (optional)**:
   ```bash
   make train
   ```

5. **Start services**:
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn app.main:app --reload

   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

6. **Access the app**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Docker Compose

```bash
# Build and start all services
docker-compose -f infra/docker-compose.yml up --build

# Or use Makefile
make docker-up
```

## 🎯 Usage

### API Endpoints

#### Risk Assessment
```bash
GET /risk?date=2024-01-15&bbox=-122,37,-121,38
```
Returns grid of 0.25° tiles with probability and CI.

#### Explanation
```bash
GET /explain?lat=37.5&lon=-122.0&date=2024-01-15
```
Returns local SHAP values, interactions, reliability bin, OOD flag.

#### Counterfactual
```bash
POST /risk/counterfactual
{
  "lat": 37.5,
  "lon": -122.0,
  "date": "2024-01-15",
  "deltas": {
    "wind_speed_10m": 20.0,
    "rh": 25.0
  },
  "use_surrogate": true
}
```
Returns new probability and delta attribution.

#### FDCF Frames
```bash
GET /frames?lat=37.5&lon=-122.0&date=2024-01-15
```
Returns FDCF frame URIs for event exploration.

#### Spread Simulation
```bash
POST /spread/run
{
  "lat": 37.5,
  "lon": -122.0,
  "date": "2024-01-15",
  "wind_speed_10m": 10.0,
  "wind_dir": 270.0,
  "duration_hours": 6,
  "steps": 12
}
```
Returns GeoJSON footprint and metrics.

## 🧪 Testing

```bash
# Run all tests
make test

# Backend only
cd backend && pytest tests/ -v

# Frontend type check
cd frontend && npm run typecheck
```

## 🔧 Development

### Linting
```bash
make lint
```

### Pre-commit Hooks
```bash
cp infra/pre-commit-config.yaml .pre-commit-config.yaml
pre-commit install
```

## 📊 Data Pipeline

### 1. Ingestion
```bash
cd etl
python ee_fdcf_ingest.py    # FDCF from Earth Engine
python weather_ingest.py     # ERA5 reanalysis
```

### 2. Labeling
```bash
python labeler.py            # Ignition events + hard negatives
```

### 3. Feature Engineering
```bash
python features_build.py     # Join to 0.25° grid, add lags
python quality.py            # DQF and availability
```

### 4. Training
```bash
cd ml
python train_gbm.py          # LightGBM with monotonicity
python calibrate.py          # Per-region calibration
python evaluate.py           # AUC-PR, Brier, ECE
python shap_report.py        # Global importances
python surrogate_train.py    # Fast emulator
python bundle.py             # Package everything
```

## 🎨 Frontend Components

- **MapHeatmap**: WebGL risk grid (deck.gl)
- **TimeScrubber**: Date selector
- **WhatIfPanel**: Sliders for wind/RH/rain/gust
- **ExplanationPanel**: SHAP waterfall + interactions
- **TriView**: Three synchronized map panels
- **EventExplorer**: FDCF frame thumbnails

## 🗂️ Data Contract

See `ml/data_contract.md` for detailed Parquet schema.

**Key features**:
- `wind_speed_10m`, `rh`, `rain_24h`, `gust_10m`
- `t2m`, `dewpoint`, `vpd`
- `recent_fires_72h_20km`
- `clim_mean`, `clim_amp`

**Label**: `ignition` (0/1)

**Quality**: `dqf_mask`, `data_availability`

## 🔬 Model Details

### Architecture
- **Primary**: LightGBM/XGBoost with monotone constraints
  - `wind_speed_10m: +1` (higher = more risk)
  - `rh: -1` (higher = less risk)
  - `rain_24h: -1` (more rain = less risk)

- **Calibration**: Isotonic regression per region
- **Surrogate**: Lightweight GBM on 4 features for fast what-if

### Evaluation Metrics
- **AUC-PR**: Area under precision-recall curve
- **Brier**: Brier score (calibration + discrimination)
- **ECE**: Expected calibration error
- **Reliability diagram**: Per-region calibration curves

## 🌐 Deployment

### Production Checklist
- [ ] Replace stub data with real FDCF/ERA5
- [ ] Train on full historical dataset (2020-2023)
- [ ] Set up model monitoring (drift detection)
- [ ] Configure autoscaling (K8s/ECS)
- [ ] Add authentication (OAuth/API keys)
- [ ] Enable HTTPS (TLS certs)
- [ ] Set up logging (ELK/Datadog)

### Environment Variables
See `.env.example` for configuration options.

## 📝 TODOs

### Backend
- [ ] Connect to real Earth Engine API
- [ ] Implement actual SHAP computation
- [ ] Add model versioning
- [ ] Cache predictions (Redis)

### ETL
- [ ] Fetch ERA5 from CDS API
- [ ] Implement proper spatial joins
- [ ] Add data validation pipeline

### ML
- [ ] Hyperparameter tuning
- [ ] Ensemble models
- [ ] Temporal cross-validation
- [ ] Feature selection

### Frontend
- [ ] Implement deck.gl heatmap layer
- [ ] Add ECharts waterfall
- [ ] Real-time updates (WebSocket)
- [ ] User authentication

## 📄 License

MIT License - see LICENSE file.

## 🙏 Attribution

This project uses data from:
- **NOAA VIIRS Active Fires** (Public domain)
- **ERA5 Reanalysis** (Copernicus Climate Change Service)
- **PRISM Climatology** (Oregon State University)

Please cite these sources when using this system.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters
5. Submit a pull request

## 📧 Contact

For questions or issues, please open a GitHub issue.

## 🔗 Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LightGBM Documentation](https://lightgbm.readthedocs.io/)
- [SHAP Documentation](https://shap.readthedocs.io/)
- [deck.gl Documentation](https://deck.gl/)

---

Built with ❤️ for wildfire risk mitigation