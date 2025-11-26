FROM python:3.11-slim AS base

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY backend/models ./models

# Copy ETL modules for GEE integration
COPY etl/__init__.py ./etl/__init__.py
COPY etl/gee_connector.py ./etl/gee_connector.py

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
