# Architecture

Mycelium follows a Hexagonal (Ports & Adapters) architecture mixed with Event-Driven principles.

## Core Components

1. **Synapse Bus (`src/micelio/core/synapse_bus.py`)**
   The heart of the application. An asynchronous Pub/Sub engine that broadcasts messages across WebSocket channels.

2. **Contract Validator (`src/micelio/services/contract_validator.py`)**
   A JSONSchema-based gatekeeper ensuring all AI agents speak the exact same structured format before polluting the bus.

3. **Quota Manager (`src/micelio/domain/billing.py`)**
   Guards API limits based on the tenant's tier (`STARTER`, `PROFESSIONAL`, `ENTERPRISE`).

4. **FastAPI Endpoints (`src/micelio/api/app.py`)**
   The presentation layer exposing HTTP and WebSocket routes.

## Performance Profile
- Uses SQLite with `PRAGMA journal_mode=WAL` for concurrent reads.
- 95%+ Test Coverage requirement enforced via GitHub Actions.
