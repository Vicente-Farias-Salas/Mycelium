"""Unit tests for configuration."""

import os
import importlib
from micelio.core import config as cfg_module
from micelio.core.config import AppConfig

def test_app_config_defaults():
    config = AppConfig()
    assert config.env == "development"
    assert config.debug is True
    assert config.rate_limit_max_events == 20

def test_app_config_from_env():
    os.environ["MYCELIUM_ENV"] = "production"
    os.environ["MYCELIUM_DEBUG"] = "false"
    os.environ["MYCELIUM_RL_MAX_EVENTS"] = "100"
    
    config = AppConfig()
    
    assert config.env == "production"
    assert config.debug is False
    assert config.rate_limit_max_events == 100
    
    # Cleanup
    del os.environ["MYCELIUM_ENV"]
    del os.environ["MYCELIUM_DEBUG"]
    del os.environ["MYCELIUM_RL_MAX_EVENTS"]
