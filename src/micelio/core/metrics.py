"""Prometheus metrics configuration and middleware for Mycelium."""

import time
from typing import Callable
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Define Metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

SYNAPSE_EVENTS_EMITTED = Counter(
    "synapse_events_emitted_total",
    "Total Synapse events emitted via API",
    ["event_type"]
)

async def metrics_middleware(request: Request, call_next: Callable) -> Response:
    """FastAPI middleware to track request counts and latency."""
    start_time = time.time()
    
    # Path categorization (avoid explosion of metrics cardinality by replacing IDs)
    path = request.url.path
    if "/api/projects/" in path and "/events" in path:
        endpoint = "/api/projects/{project_id}/events"
    elif "/api/tenants/" in path and "/predict-churn" in path:
        endpoint = "/api/tenants/{tenant_id}/predict-churn"
    else:
        endpoint = path
        
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        raise e
    finally:
        latency = time.time() - start_time
        REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, http_status=status_code).inc()
        REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(latency)
        
    return response

def get_metrics_response() -> Response:
    """Generate the Prometheus metrics response."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
