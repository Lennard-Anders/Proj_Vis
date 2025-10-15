"""
FastAPI main application for Multimodal Wildfire Risk Modeling
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_risk, routes_explain, routes_counterfactual, routes_frames, routes_spread

app = FastAPI(
    title="Wildfire Risk API",
    description="Multimodal Wildfire Risk Modeling for Americas",
    version="0.1.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes_risk.router, prefix="/risk", tags=["risk"])
app.include_router(routes_explain.router, prefix="/explain", tags=["explain"])
app.include_router(routes_counterfactual.router, prefix="/risk", tags=["counterfactual"])
app.include_router(routes_frames.router, prefix="/frames", tags=["frames"])
app.include_router(routes_spread.router, prefix="/spread", tags=["spread"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Wildfire Risk API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
