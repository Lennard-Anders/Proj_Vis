from functools import lru_cache

from .core.config import get_settings
from .models.registry import ModelBundleRegistry


@lru_cache(1)
def get_registry() -> ModelBundleRegistry:
    settings = get_settings()
    return ModelBundleRegistry(bundle_path=settings.model_bundle_path)
