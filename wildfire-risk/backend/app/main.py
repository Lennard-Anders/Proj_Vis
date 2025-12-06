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
    routes_gee,
    routes_fire_history,
    routes_temperature,
    routes_ai_risk,
    routes_wildfire_llm,
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
app.include_router(routes_gee.router, prefix="/api")
app.include_router(routes_fire_history.router, prefix="/api")
app.include_router(routes_temperature.router, prefix="/api")
app.include_router(routes_ai_risk.router, prefix="/api")
app.include_router(routes_wildfire_llm.router, prefix="/api")

# Add Prometheus instrumentation before app starts
Instrumentator().instrument(app).expose(app)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
