from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import risk, explain, frames, spread

app = FastAPI(
    title="Wildfire Risk API",
    description="API for wildfire risk prediction and explainability",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(risk.router, prefix="/risk", tags=["risk"])
app.include_router(explain.router, prefix="/explain", tags=["explain"])
app.include_router(frames.router, prefix="/frames", tags=["frames"])
app.include_router(spread.router, prefix="/spread", tags=["spread"])


@app.get("/")
async def root():
    return {
        "message": "Wildfire Risk API",
        "version": "0.1.0",
        "endpoints": [
            "/risk",
            "/explain",
            "/risk/counterfactual",
            "/frames",
            "/spread"
        ]
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
