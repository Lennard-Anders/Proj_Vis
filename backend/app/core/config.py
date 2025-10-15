"""
Core configuration settings
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    api_title: str = "Wildfire Risk API"
    api_version: str = "0.1.0"
    
    # Model Settings
    model_bundle_path: str = "/backend/models/bundles/model_bundle"
    
    # Data Settings
    data_dir: str = "/data"
    
    # Optional external API tokens
    mapbox_token: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False
