# API Reference

## Authentication

All protected endpoints require a Bearer JWT Token or the Master API Key in the `X-Mycelium-API-Key` header.

### `POST /api/token`
Generates a JWT token for a specific subject.

## Core Endpoints

### `GET /health`
Returns the system status, SQLite reachability, and memory usage.

### `POST /api/tenants`
Registers a new commercial tenant in the system to enable project quotas.

### `POST /api/projects`
Creates a new `LivingProject` swarm if the tenant hasn't exceeded their quota.

### `GET /api/analytics/overview`
Retrieves live counts of active projects and total events fired.

## WebSocket Streaming

### `WS /ws/analytics/live`
Unidirectional live feed of raw `SynapseEvent` structs streaming in real-time.
