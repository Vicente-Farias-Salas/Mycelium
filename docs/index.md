# Welcome to Mycelium Enterprise

Mycelium is an Agent-to-Agent (A2A) Coordination Substrate designed for Enterprise workflows.

## Concept

Instead of interacting with isolated AIs, Mycelium provides a "Virtual Office" (`SynapseBus`) where human agents (swarms of workers) coordinate to solve complex problems.

## Features

- **SynapseBus**: High-throughput WebSocket message bus for Agents.
- **SQLite WAL**: 10k ops/sec native storage engine.
- **Tenancy Quotas**: Real-time project billing and multi-tenant quotas.
- **JWT Authentication**: Enterprise-grade security via stateless tokens.
- **Cyberpunk Telemetry**: A glowing, fast-reacting frontend interface.

## Quick Start

```bash
# Start the backend server
make run

# Run test suite
make test

# Build the pip wheel
make build
```
