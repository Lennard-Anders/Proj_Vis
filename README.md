# Wildfire Risk Visualization Platform

A comprehensive monorepo for wildfire risk prediction, visualization, and explainability using machine learning and interactive web technologies.

## 🏗️ Architecture

This project is organized as a monorepo with the following components:

```
Proj_Vis/
├── backend/          # FastAPI REST API for risk prediction
├── frontend/         # React + Vite + deck.gl visualization
├── etl/             # Data ingestion and feature engineering
├── ml/              # Machine learning training and evaluation
├── docker/          # Docker configurations
└── .github/         # CI/CD workflows
```

## 🚀 Features

### Backend (Python 3.11 + FastAPI)
- **Risk Prediction API** (`/risk`): Predict wildfire risk based on environmental conditions
- **Explainability API** (`/explain`): SHAP-based feature importance explanations
- **Counterfactual API** (`/risk/counterfactual`): What-if scenario analysis
- **Frames API** (`/frames`): Temporal wildfire spread visualization
- **Spread API** (`/spread`): Spatial fire spread prediction
- Model bundle loader with calibration
- Surrogate model for fast inference

### ETL Pipeline
- **FDCF/Weather Ingestion**: Fetch and process fire danger and weather data
- **Labeler**: Create training labels from historical fire data
- **Feature Engineering**: Generate features at 0.25° spatial resolution
  - Temporal features (seasonality, time-of-day)
  - Weather-derived features (VPD, drought indices)
  - Vegetation indices (NDVI, EVI)
  - Lag and rolling window features

### ML Training
- **Gradient Boosting Machine** with monotone constraints
  - Temperature ↑ increases risk
  - Humidity ↓ decreases risk
  - Wind speed ↑ increases risk
  - Precipitation ↓ decreases risk
- **Calibration**: Isotonic regression and Platt scaling
- **Evaluation**: Comprehensive metrics and spatial/temporal analysis
- **Surrogate Model**: Fast neural network approximation for real-time inference

### Frontend (React + Vite + deck.gl)
- **Interactive Map**: Heatmap visualization of wildfire risk
- **Tri-View Timeline**: Multi-perspective temporal analysis
  - Risk score evolution
  - Spread patterns
  - Fire intensity
- **What-If Panel**: Interactive scenario exploration
  - Adjust environmental parameters
  - See real-time risk predictions
- **XAI Panel**: Explainable AI insights
  - SHAP feature contributions
  - Counterfactual explanations

## 🛠️ Installation

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 20+
- Make (optional, for convenience commands)

### Quick Start with Docker

```bash
# Build all containers
make build

# Start backend and frontend services
make up

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### ETL
```bash
cd etl
pip install -r requirements.txt
python -m src.ingest.fdcf_weather
```

#### ML Training
```bash
cd ml
pip install -r requirements.txt
# Training scripts in src/training/
```

## 📋 Available Commands

```bash
make help              # Show all available commands
make install           # Install all dependencies
make build             # Build Docker containers
make up                # Start services
make down              # Stop services
make test              # Run all tests
make lint              # Run linters
make clean             # Clean build artifacts

# Component-specific
make backend-test      # Test backend
make frontend-test     # Test frontend
make etl-test          # Test ETL
make ml-test           # Test ML
make dev-backend       # Run backend in dev mode
make dev-frontend      # Run frontend in dev mode
make run-etl           # Execute ETL pipeline
make run-training      # Run ML training
make logs              # View all logs
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
```

### ETL Tests
```bash
cd etl
pytest tests/ -v
```

### ML Tests
```bash
cd ml
pytest tests/ -v
```

## 📊 API Documentation

When the backend is running, interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Example API Calls

#### Predict Risk
```bash
curl -X POST "http://localhost:8000/risk/" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 37.0,
    "longitude": -120.0,
    "temperature": 32.0,
    "humidity": 25.0,
    "wind_speed": 15.0,
    "precipitation": 0.0,
    "vegetation_index": 0.6,
    "fuel_moisture": 8.0
  }'
```

#### Get Explanation
```bash
curl -X POST "http://localhost:8000/explain/" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 37.0,
    "longitude": -120.0,
    "temperature": 32.0,
    "humidity": 25.0,
    "wind_speed": 15.0,
    "precipitation": 0.0,
    "vegetation_index": 0.6,
    "fuel_moisture": 8.0
  }'
```

## 🔧 Configuration

### Environment Variables

#### Backend
```bash
MODEL_PATH=/models/wildfire_model.pkl
PYTHONUNBUFFERED=1
```

#### Frontend
```bash
VITE_API_URL=http://localhost:8000
```

## 🏃 CI/CD

GitHub Actions workflows are configured for:
- Backend testing and coverage
- Frontend build and testing
- ETL testing
- ML testing
- Docker build verification

## 📦 Project Structure

```
Proj_Vis/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── routes/              # API endpoints
│   │   │   ├── risk.py
│   │   │   ├── explain.py
│   │   │   ├── frames.py
│   │   │   └── spread.py
│   │   └── services/            # Business logic
│   │       ├── model_loader.py
│   │       ├── calibration.py
│   │       ├── shap_explainer.py
│   │       └── surrogate.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MapComponent.jsx
│   │   │   ├── TriViewTimeline.jsx
│   │   │   ├── WhatIfPanel.jsx
│   │   │   └── XAIPanel.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── etl/
│   ├── src/
│   │   ├── ingest/              # Data ingestion
│   │   │   └── fdcf_weather.py
│   │   ├── labeler/             # Label creation
│   │   │   └── fire_labeler.py
│   │   └── features/            # Feature engineering
│   │       └── feature_engineering.py
│   └── requirements.txt
├── ml/
│   ├── src/
│   │   ├── training/            # Model training
│   │   │   └── gbm_trainer.py
│   │   ├── calibration/         # Calibration
│   │   │   └── calibrator.py
│   │   ├── evaluation/          # Metrics
│   │   │   └── metrics.py
│   │   └── surrogate/           # Surrogate models
│   │       └── surrogate_model.py
│   └── requirements.txt
├── docker-compose.yml
├── Makefile
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Fire danger data from FDCF
- Weather data from NOAA/ERA5
- Historical fire data from NIFC/MTBS
- deck.gl for geospatial visualization
- SHAP for model explainability

## 📧 Contact

For questions or support, please open an issue on GitHub.