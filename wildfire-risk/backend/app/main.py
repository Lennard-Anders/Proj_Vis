from __future__ import annotations

import logging.config
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from .api import (
    routes_counterfactual,
    routes_explain,
    routes_frames,
    routes_risk,
    routes_spread,
)
from .core.config import get_settings

LOGGING_CONFIG = Path(__file__).parent / "core" / "logging.conf"
if LOGGING_CONFIG.exists():
    logging.config.fileConfig(LOGGING_CONFIG, disable_existing_loggers=False)

settings = get_settings()
app = FastAPI(title=settings.app_name)

if settings.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

app.include_router(routes_risk.router, prefix="/api")
app.include_router(routes_explain.router, prefix="/api")
app.include_router(routes_counterfactual.router, prefix="/api")
app.include_router(routes_frames.router, prefix="/api")
app.include_router(routes_spread.router, prefix="/api")

# Add Prometheus instrumentation before app starts
Instrumentator().instrument(app).expose(app)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
