"""Application configuration management for Mycelium."""

import os
from typing import Any
from pydantic import BaseModel, Field

class AppConfig(BaseModel):
    """Global application settings initialized from environment variables."""
    
    # Environment
    env: str = Field(default_factory=lambda: os.getenv("MYCELIUM_ENV", "development"))
    debug: bool = Field(default_factory=lambda: os.getenv("MYCELIUM_DEBUG", "True").lower() in ("true", "1", "yes"))
    
    # Security
    api_key: str = Field(default_factory=lambda: os.getenv("MYCELIUM_API_KEY", "default_dev_key_super_secret"))
    
    # Storage
    db_path: str = Field(default_factory=lambda: os.getenv("MYCELIUM_DB_PATH", "data/micelio.db"))
    workspace_base_dir: str = Field(default_factory=lambda: os.getenv("MYCELIUM_WORKSPACE_DIR", "proyectos"))
    
    # Rate Limiting
    rate_limit_max_events: int = Field(default_factory=lambda: int(os.getenv("MYCELIUM_RL_MAX_EVENTS", "20")))
    rate_limit_window_seconds: float = Field(default_factory=lambda: float(os.getenv("MYCELIUM_RL_WINDOW", "1.0")))

# Global singleton
config = AppConfig()
