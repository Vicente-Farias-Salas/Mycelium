"""System health and basic profiling metrics."""

import time
import threading
import platform
from typing import Any

START_TIME = time.time()

def get_system_health() -> dict[str, Any]:
    """Retrieve basic health and diagnostic metrics using standard libraries."""
    uptime_seconds = time.time() - START_TIME
    
    return {
        "status": "pass",
        "uptime_seconds": round(uptime_seconds, 2),
        "active_threads": threading.active_count(),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "system": platform.system(),
        "machine": platform.machine()
    }
