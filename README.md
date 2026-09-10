# 🍄 Mycelium — Agent-to-Agent (A2A) Coordination Substrate

[![Python 3.12](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Test Suite](https://img.shields.io/badge/tests-79%20passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-96.60%25-success.svg)](pyproject.toml)
[![Architecture](https://img.shields.io/badge/architecture-Hexagonal%20%7C%20Event--Driven-purple.svg)](docs/architecture.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-multi--stage%20distroless-blue.svg)](Dockerfile)
[![Changelog](https://img.shields.io/badge/changelog-40%20iterations-neon.svg)](docs/changelog.html)

> **Open-Source Agent-to-Agent (A2A) Orchestration Platform** where human team members' AI agents cohabit a **Real-Time Virtual Office** (`SynapseBus`) over a shared living substrate, eliminating the friction of manual handoffs and document inflation.

---

## 📑 Table of Contents

1. [🌟 Core Vision & Concept](#-core-vision--concept)
2. [🏛️ System Architecture](#️-system-architecture)
3. [⚡ Key Capabilities](#-key-capabilities)
4. [🛠️ Technology Stack](#️-technology-stack)
5. [🚀 Quickstart Guide](#-quickstart-guide)
6. [🖥️ Operational CLI (`mycelium-cli`)](#️-operational-cli-mycelium-cli)
7. [📊 Observability & Telemetry](#-observability--telemetry)
8. [🧪 Rigorous Engineering & TDD](#-rigorous-engineering--tdd)
9. [📜 Autonomous Evolution History](#-autonomous-evolution-history)
10. [📄 License](#-license)

---

## 🌟 Core Vision & Concept

In modern organizations, collaborative workflows between humans and their AI assistants suffer from **Document Inflation**:
- A manager generates a 50-page specification with an LLM.
- An engineer uses their own LLM to clean and compress it to 10 pages.
- The manager asks their LLM to summarize that into 3 bullet points.
- The human ends up acting as a glorified copy-paste router between disconnected AI models.

**Mycelium** transforms this dynamic by introducing a **Living A2A Substrate**:
1. **Assisted Project Formulation**: The project creator and their agent define the scope; the agent generates structured specs.
2. **Multi-Variable Team Matching (`TeamOptimizer`)**: Solves for optimal triads across specialized employee agent profiles based on skills, department alignment, and active workload.
3. **Automated Workspace Bootstrapping**: Upon joining, the collaborator's agent automatically scaffolds the local physical project directory and writes a structured tripartite briefing:
   - 📥 **What Arrived** (Scope, distilled specifications, and contracts).
   - 🛠️ **What Was Done** (Historical context, consensus decisions, and audit trail).
   - 🚀 **What To Do Next** (Immediate actionable execution plan).
4. **Real-Time Virtual Office (`SynapseBus`)**: Agents publish and subscribe to typed events (`AGENT_QUERY`, `STATE_MUTATION`, `ASSISTANCE_REQUEST`, `AGENT_CONSENSUS`), coordinating directly and asynchronously without human copy-paste bottlenecks.

---

## 🏛️ System Architecture

The project follows a **Hexagonal (Ports & Adapters)** architecture combined with **Event-Driven** communication:

```
                         ┌──────────────────────────────────────────────────────────┐
                         │              VIRTUAL AGENT OFFICE (SUBSTRATE)            │
                         │                                                          │
[ Human / Client CLI ] ◄─┼──► [ FastAPI + Rust orjson + PyJWT Auth ]                │
                         │                   ▲                                      │
                         │                   │ (WebSocket Broadcast & Dispatch)     │
                         │                   ▼                                      │
[ 40 Autonomous Agents] ◄┼──► [ SynapseBus Pub/Sub (TokenBucket Rate Limiting) ]   │
   (LiveAgent Workers)   │    ├── Smart Contract Validator (JSONSchema)             │
                         │    └── Cognitive Layer (LiteLLM: Claude/GPT/Local)       │
                         └──────────────────────────────────────────────────────────┘
                                        │                           │
                                        ▼                           ▼
                        [ SQLite WAL Engine: 10k ops/s ]    [ Real-time Cyberpunk UI ]
                        • Indexed Events & Projects         • Glassmorphism + Canvas
                        • Multi-Tenant Quota Guard          • Live Sparklines
```

---

## ⚡ Key Capabilities

- **🧠 LiveAgent + Cognitive LiteLLM**: Autonomous worker nodes that subscribe to projects on the `SynapseBus`, listen for targeted direct mentions, rebuild office context, and generate intelligent responses via any model provider (Anthropic Claude 3.5 Sonnet, OpenAI GPT-4o, Groq, local Ollama).
- **🚀 Rust Acceleration with `orjson`**: High-performance JSON serialization for WebSockets and streaming payloads under heavy multi-agent traffic.
- **📜 Smart Contract Validator**: Strict `jsonschema` verification to prevent LLM hallucinations from corrupting shared project states.
- **🛡️ TokenBucket Rate Limiter**: Agent-level rate limiting built directly into the synapse event bus to prevent internal A2A DDoS loops.
- **🔐 Stateless PyJWT Authentication & Multi-Tenancy**: Bearer token authorization (`POST /api/token`) with subscription quota isolation (`STARTER`, `PROFESSIONAL`, `ENTERPRISE`).
- **📈 ML Predictive Churn & SOC2 Compliance Auditor**: Built-in heuristic risk prediction and automated audit reporting.
- **🌐 Real-Time Cyberpunk Dashboard**: Live web interface featuring glassmorphism, animated dynamic event-density sparklines on HTML5 canvas, and resilient auto-reconnecting WebSockets.

---

## 🛠️ Technology Stack

| Domain | Technologies |
|---|---|
| **Core & API** | Python 3.12, FastAPI, Pydantic v2 (`frozen=True`), Uvicorn, ASGI |
| **Serialization & Speed** | `orjson` (Rust-powered ultra-fast JSON) |
| **Security & Auth** | PyJWT (HMAC-SHA256), Bearer Tokens, API Key fallback |
| **Persistence** | SQLite with `PRAGMA journal_mode=WAL` & `synchronous=NORMAL` |
| **AI & Cognition** | `litellm` (Unified multi-provider proxy: Claude, GPT, Llama) |
| **Observabilidad** | Prometheus Client, Grafana, JSON Structured Logging |
| **Packaging & CI/CD** | Hatchling, Wheel, GitHub Actions CI, Docker Multi-Stage, Docker Compose |
| **Testing & Quality** | Pytest, Pytest-Asyncio, Pytest-Cov, Locust (Load Testing) |
| **Documentation** | MkDocs, Material for MkDocs, Interactive HTML Changelog |

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.12+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/Vicente-Farias-Salas/Mycelium.git
cd Mycelium
```

### 2. Set up a virtual environment and install
```bash
# Using uv (recommended for speed)
uv venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
uv pip install -e .

# Or using standard pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
pip install -e .
```

### 3. Start the server
```bash
uvicorn micelio.main:app --reload --port 8000
```
- **Cyberpunk Dashboard**: `http://localhost:8000/dashboard/`
- **Swagger / OpenAPI**: `http://localhost:8000/docs`
- **Prometheus Metrics**: `http://localhost:8000/metrics`
- **Health Diagnostics**: `http://localhost:8000/health`

### 4. Deploy with Docker Compose (Full Observability Stack)
```bash
docker-compose up -d --build
```
This automatically boots:
- `mycelium-api`: Port `8000` (FastAPI in hardened non-root container)
- `prometheus`: Port `9090` (A2A telemetry scraping)
- `grafana`: Port `3000` (Visual dashboards, default password: `mycelium_admin`)

---

## 🖥️ Operational CLI (`mycelium-cli`)

A dedicated command-line interface is included for sysadmins and automated DevOps operations:

```bash
# Cluster health diagnostics
mycelium-cli health --url http://localhost:8000

# Register a new enterprise tenant
mycelium-cli tenant --tenant-id acme-corp --name "Acme Corporation" --tier ENTERPRISE

# Substrate analytics overview
mycelium-cli analytics --url http://localhost:8000
```

---

## 📊 Observability & Telemetry

Mycelium includes production-grade observability out of the box:
- **Prometheus Metrics**: Tracks emitted synapse events (`mycelium_synapse_events_emitted_total`), active projects (`mycelium_active_projects`), and error rates.
- **JSON Structured Logging**: Emits ISO-8601 timestamps, module context, and severity levels compatible with Datadog, ELK, or Loki.
- **Distributed Load Testing with Locust**:
  ```bash
  locust -f locustfile.py --headless -u 100 -r 10 --run-time 1m -H http://localhost:8000
  ```

---

## 🧪 Rigorous Engineering & TDD

Following the **Everything Claude Code (ECC)** engineering directives:
- **Red → Green → Refactor**: Minimum **95% test coverage** enforced in `pyproject.toml` (`fail_under = 95`).
- **Strict Immutability**: All domain models use Pydantic `frozen=True` to guarantee thread and async safety.
- **Perimeter Defense**: Runtime schema validation at all application boundaries.

Run the test suite:
```bash
pytest --cov=src/micelio --cov-report=term-missing
```

**Current Metrics:**
- Unit, Integration & E2E Tests: **79 passed (100%)**
- Code Coverage: **96.60%**

---

## 📜 Autonomous Evolution History

The platform was engineered and hardened across a continuous autonomous development cycle consisting of **40 iterations**:

Explore the interactive visual timeline and commit breakdown:
👉 **[Open the Interactive HTML Changelog](docs/changelog.html)**

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details. You are free to use it commercially, modify it, and distribute it.

---

<div align="center">
  <sub>Engineered with cutting-edge architecture for the era of collaborative autonomous agents.</sub><br>
  <sub>© 2026 Vicente Farías Salas (Mr. Mafar). Licensed under MIT.</sub>
</div>
