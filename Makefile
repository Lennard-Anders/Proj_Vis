.PHONY: help etl train serve test clean install

help:
	@echo "Wildfire Risk Modeling - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install     - Install all dependencies"
	@echo "  etl         - Run ETL pipeline"
	@echo "  train       - Train model"
	@echo "  serve       - Start backend and frontend servers"
	@echo "  test        - Run all tests"
	@echo "  lint        - Run linters"
	@echo "  clean       - Clean build artifacts"

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing ETL dependencies..."
	cd etl && pip install -r requirements.txt
	@echo "Installing ML dependencies..."
	cd ml && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Installation complete!"

etl:
	@echo "Running ETL pipeline..."
	cd etl && python labeler.py
	cd etl && python features_build.py
	@echo "ETL complete!"

train:
	@echo "Training model..."
	cd ml && python train_gbm.py
	cd ml && python calibrate.py
	cd ml && python evaluate.py
	cd ml && python surrogate_train.py
	cd ml && python bundle.py
	@echo "Training complete!"

serve:
	@echo "Starting services..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	docker-compose -f infra/docker-compose.yml up

serve-dev:
	@echo "Starting development servers..."
	@echo "Run in separate terminals:"
	@echo "  Terminal 1: cd backend && uvicorn app.main:app --reload"
	@echo "  Terminal 2: cd frontend && npm run dev"

test:
	@echo "Running backend tests..."
	cd backend && pytest tests/ -v
	@echo "Running frontend type checks..."
	cd frontend && npm run typecheck
	@echo "All tests passed!"

lint:
	@echo "Running linters..."
	cd backend && black . && ruff check .
	cd frontend && npm run lint
	@echo "Linting complete!"

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf backend/.pytest_cache
	rm -rf frontend/dist
	rm -rf frontend/node_modules
	@echo "Clean complete!"

docker-build:
	@echo "Building Docker images..."
	docker-compose -f infra/docker-compose.yml build

docker-up:
	@echo "Starting Docker containers..."
	docker-compose -f infra/docker-compose.yml up -d

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose -f infra/docker-compose.yml down

docker-logs:
	docker-compose -f infra/docker-compose.yml logs -f
