.PHONY: help install build up down test lint clean backend-test frontend-test etl-test ml-test

help:
	@echo "Wildfire Risk Monorepo - Available Commands"
	@echo "============================================"
	@echo "make install          - Install all dependencies"
	@echo "make build            - Build all Docker containers"
	@echo "make up               - Start all services"
	@echo "make down             - Stop all services"
	@echo "make test             - Run all tests"
	@echo "make lint             - Run all linters"
	@echo "make clean            - Clean build artifacts"
	@echo ""
	@echo "Component-specific commands:"
	@echo "make backend-test     - Run backend tests"
	@echo "make frontend-test    - Run frontend tests"
	@echo "make etl-test         - Run ETL tests"
	@echo "make ml-test          - Run ML tests"

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Installing ETL dependencies..."
	cd etl && pip install -r requirements.txt
	@echo "Installing ML dependencies..."
	cd ml && pip install -r requirements.txt

build:
	@echo "Building Docker containers..."
	docker-compose build

up:
	@echo "Starting services..."
	docker-compose up -d backend frontend
	@echo "Services started. Frontend: http://localhost:3000, Backend: http://localhost:8000"

down:
	@echo "Stopping services..."
	docker-compose down

test: backend-test frontend-test etl-test ml-test

backend-test:
	@echo "Running backend tests..."
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing

frontend-test:
	@echo "Running frontend tests..."
	cd frontend && npm test

etl-test:
	@echo "Running ETL tests..."
	cd etl && pytest tests/ -v

ml-test:
	@echo "Running ML tests..."
	cd ml && pytest tests/ -v

lint:
	@echo "Linting backend..."
	cd backend && python -m pylint app/ || true
	@echo "Linting frontend..."
	cd frontend && npm run lint || true
	@echo "Linting ETL..."
	cd etl && python -m pylint src/ || true
	@echo "Linting ML..."
	cd ml && python -m pylint src/ || true

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	cd frontend && rm -rf dist node_modules/.vite 2>/dev/null || true
	@echo "Clean complete"

dev-backend:
	@echo "Starting backend in dev mode..."
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend in dev mode..."
	cd frontend && npm run dev

run-etl:
	@echo "Running ETL pipeline..."
	docker-compose --profile etl up etl

run-training:
	@echo "Running ML training..."
	docker-compose --profile training up ml-training

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend
