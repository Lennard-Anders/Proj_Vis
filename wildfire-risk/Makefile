.PHONY: etl features train calibrate eval bundle serve ui up test fmt lint

PYTHON?=python
NPM?=npm

etl: ## runs synthetic FDCF + weather ingestion
	$(PYTHON) -m etl.ee_fdcf_ingest
	$(PYTHON) -m etl.weather_ingest

features: ## builds synthetic feature tiles
	$(PYTHON) -m etl.features_build

train: ## trains synthetic gradient boosted model
	$(PYTHON) -m ml.train_gbm

calibrate: ## calibrates synthetic probabilities
	$(PYTHON) -m ml.calibrate

eval: ## evaluates model metrics
	$(PYTHON) -m ml.evaluate

bundle: ## assembles the model bundle artifact
	$(PYTHON) -m ml.bundle

serve: ## runs backend with reload
	uvicorn backend.app.main:app --reload --port 8000

ui: ## runs frontend dev server
	cd frontend && $(NPM) install && $(NPM) run dev

up: ## runs the entire local stack
	docker-compose up --build

test: ## runs backend and frontend tests
	pytest -q
	cd frontend && $(NPM) install && $(NPM) test

fmt: ## formats sources via pre-commit
	pre-commit run --all-files

lint: ## lint + type check
	pre-commit run --all-files
