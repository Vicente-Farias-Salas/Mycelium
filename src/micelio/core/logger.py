"""Structured JSON Logger for Enterprise Observability."""

import json
import logging
from datetime import datetime, timezone
from typing import Any

class JSONFormatter(logging.Formatter):
    """Format log records as strict JSON for log aggregators (Splunk/Datadog/ELK)."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Include exception traceback if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Include any extra kwargs passed to the logger
        if hasattr(record, "extra_ctx"):
            log_obj["context"] = record.extra_ctx

        return json.dumps(log_obj)

def setup_json_logger(name: str = "micelio", level: int = logging.INFO) -> logging.Logger:
    """Initialize and return a structured JSON logger."""
    logger = logging.getLogger(name)
    
    # Prevent attaching multiple handlers in a dev/reload environment
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
        
    return logger

# Global instance
logger = setup_json_logger()
