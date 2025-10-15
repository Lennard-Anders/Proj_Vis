"""
Dependency injection helpers for FastAPI
"""
from functools import lru_cache

from app.core.config import Settings
from app.models.registry import ModelRegistry


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings"""
    return Settings()


@lru_cache()
def get_model_registry() -> ModelRegistry:
    """Get cached model registry"""
    return ModelRegistry()
