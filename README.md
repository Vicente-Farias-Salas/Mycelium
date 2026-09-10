# 🍄 Mycelium Enterprise — Agent-to-Agent (A2A) Coordination Substrate

[![Python 3.12](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Test Suite](https://img.shields.io/badge/tests-79%20passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-96.60%25-success.svg)](pyproject.toml)
[![Architecture](https://img.shields.io/badge/architecture-Hexagonal%20%7C%20Event--Driven-purple.svg)](docs/architecture.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-ea4aaa?logo=GitHub-Sponsors)](https://github.com/sponsors/Vicente-Farias-Salas)
[![Docker](https://img.shields.io/badge/docker-multi--stage%20distroless-blue.svg)](Dockerfile)
[![Changelog](https://img.shields.io/badge/changelog-40%20iterations-neon.svg)](docs/changelog.html)

> **Plataforma Enterprise B2B de Orquestación Agente-a-Agente (A2A)** donde los agentes personales y de enjambre cohabitan una **Oficina Virtual en Tiempo Real** (`SynapseBus`) sobre un sustrato vivo compartido, eliminando la fricción de traspasos manuales y la inflación documental.

---

## 📑 Tabla de Contenidos

1. [🌟 Visión y Concepto](#-visión-y-concepto)
2. [🏛️ Arquitectura del Sistema](#️-arquitectura-del-sistema)
3. [⚡ Capacidades Principales](#-capacidades-principales)
4. [🛠️ Ecosistema Tecnológico](#️-ecosistema-tecnológico)
5. [🚀 Guía de Inicio Rápido](#-guía-de-inicio-rápido)
6. [🖥️ CLI Operacional (`mycelium-cli`)](#️-cli-operacional-mycelium-cli)
7. [📊 Observabilidad y Telemetría](#-observabilidad-y-telemetría)
8. [🧪 Pruebas y Rigor de Ingeniería (TDD)](#-pruebas-y-rigor-de-ingeniería-tdd)
9. [📜 Historial de Evolución Autónoma](#-historial-de-evolución-autónoma)
10. [💖 Apoya el Proyecto (GitHub Sponsors)](#-apoya-el-proyecto-github-sponsors)
11. [📄 Licencia](#-licencia)

---

## 🌟 Visión y Concepto

En las organizaciones contemporáneas, el flujo de trabajo entre humanos y sus inteligencias artificiales sufre de **inflación y dispersión documental**:
- Un directivo genera un documento de 50 páginas con su IA.
- El colaborador limpia y comprime a 10 páginas con su propia IA.
- El directivo solicita a su IA resumir todo en 3 viñetas.
- El humano actúa como un simple intermediario manual de copiar y pegar.

**Mycelium** transforma esta dinámica instaurando un **Sustrato Vivo A2A**:
1. **Concepción Asistida**: El directivo y su agente formulan el proyecto; el agente genera la síntesis estructurada.
2. **Matching Multivariable de Equipos (`TeamOptimizer`)**: Analiza las competencias requeridas, departamento y carga de 40 colaboradores para orquestar la tríada ideal.
3. **Bootstrapping Automatizado del Workspace**: El agente del colaborador inicializa localmente el entorno de trabajo y redacta el informe tripartito:
   - 📥 **¿Qué llegó?** (Alcance, especificaciones y contratos).
   - 🛠️ **¿Qué se ha hecho?** (Historial, decisiones y auditorías).
   - 🚀 **¿Qué podemos hacer?** (Plan de ejecución inmediato).
4. **Oficina Virtual en Tiempo Real (`SynapseBus`)**: Los agentes publican y consumen eventos tipados de consulta, propuesta y consenso, coordinándose de forma directa y asíncrona.

---

## 🏛️ Arquitectura del Sistema

El proyecto sigue una arquitectura **Hexagonal (Ports & Adapters)** combinada con principios **Event-Driven**:

```
                         ┌──────────────────────────────────────────────────────────┐
                         │              VIRTUAL AGENT OFFICE (SUBSTRATE)            │
                         │                                                          │
[ Human / Client CLI ] ◄─┼──► [ FastAPI 0.141+ + Rust orjson + PyJWT Auth ]         │
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

## ⚡ Capacidades Principales

- **🧠 LiveAgent + Cognitive LiteLLM**: Nodos autónomos de agente que se suscriben a proyectos en el `SynapseBus`, reaccionan a menciones directas, reconstruyen el contexto de la oficina y generan respuestas inteligentes mediante modelos de lenguaje (OpenAI, Anthropic Claude, Groq, Ollama).
- **🚀 Aceleración Rust con `orjson`**: Serialización de alto rendimiento para WebSockets y respuestas JSON ultrarrápidas bajo tráfico pesado.
- **📜 Validador de Contratos Inteligentes**: Validador estricto basado en `jsonschema` que previene alucinaciones o degradación del protocolo en los mensajes del bus.
- **🛡️ TokenBucket Rate Limiter**: Protección anti-DDoS integrada a nivel de agente en el bus de sinapsis.
- **🔐 Autenticación JWT Stateless & Multi-Tenancy**: Emisión de Bearer tokens (`POST /api/token`) con aislamiento estricto de cuotas por nivel de suscripción (`STARTER`, `PROFESSIONAL`, `ENTERPRISE`).
- **📈 ML Predictive Churn & SOC2 Compliance Auditor**: Algoritmos heurísticos de predicción de riesgo y auditoría de cumplimiento normativo integrados en la API.
- **🌐 Portal Web Cyberpunk**: Dashboard en tiempo real con estética terminal dark, glassmorphism, sparklines dinámicos de densidad de eventos y reconexión resiliente a WebSockets.

---

## 🛠️ Ecosistema Tecnológico

| Dominio | Tecnologías |
|---|---|
| **Core & API** | Python 3.12, FastAPI, Pydantic v2 (`frozen=True`), Uvicorn, ASGI |
| **Aceleración & Serialización** | `orjson` (Rust-powered JSON) |
| **Seguridad & Auth** | PyJWT (HMAC-SHA256), Bearer Tokens, API Key Fallback |
| **Persistencia** | SQLite nativo en modo `PRAGMA journal_mode=WAL`, `synchronous=NORMAL` |
| **IA & Cognición** | `litellm` (Proxy multi-proveedor: Claude 3.5, GPT-4o, Llama 3) |
| **Observabilidad** | Prometheus Client, Grafana, JSON Structured Logging (`logging`) |
| **Packaging & CI/CD** | Hatchling, Wheel, GitHub Actions CI, Docker Multi-Stage, Docker Compose |
| **Testing & Calidad** | Pytest, Pytest-Asyncio, Pytest-Cov, Locust (Load Testing) |
| **Documentación** | MkDocs, Material for MkDocs, Changelog HTML interactivo |

---

## 🚀 Guía de Inicio Rápido

### Prerrequisitos
- Python 3.12+ instalado
- Git

### 1. Clonar el repositorio
```bash
git clone https://github.com/Vicente-Farias-Salas/Mycelium.git
cd Mycelium
```

### 2. Configurar el entorno virtual e instalar
```bash
# Con uv (recomendado)
uv venv
.\.venv\Scripts\activate
uv pip install -e .

# O con pip tradicional
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
```

### 3. Ejecutar el servidor
```bash
uvicorn micelio.api.app:app --reload --port 8000
```
- **Dashboard Cyberpunk**: `http://localhost:8000/dashboard`
- **Swagger / OpenAPI**: `http://localhost:8000/docs`
- **Métricas Prometheus**: `http://localhost:8000/metrics`
- **Diagnóstico de Salud**: `http://localhost:8000/health`

### 4. Despliegue con Docker Compose (Full Observability Stack)
```bash
docker-compose up -d --build
```
Levanta automáticamente:
- `mycelium-api`: Puerto `8000` (FastAPI en contenedor optimizado non-root)
- `prometheus`: Puerto `9090` (Scraping de telemetría A2A)
- `grafana`: Puerto `3000` (Dashboards visuales, clave inicial: `mycelium_admin`)

---

## 🖥️ CLI Operacional (`mycelium-cli`)

El paquete incluye una interfaz de línea de comandos para administradores de sistemas y automatización DevOps:

```bash
# Diagnóstico de salud del clúster
mycelium-cli health --url http://localhost:8000

# Registro de un nuevo Tenant empresarial
mycelium-cli tenant --tenant-id acme-corp --name "Acme Corporation" --tier ENTERPRISE

# Resumen de analíticas del sustrato
mycelium-cli analytics --url http://localhost:8000
```

---

## 📊 Observabilidad y Telemetría

Mycelium implementa observabilidad integral de primer nivel:
- **Métricas Prometheus**: Contador de eventos emitidos (`mycelium_synapse_events_emitted_total`), proyectos activos (`mycelium_active_projects`), y tasa de error.
- **Logs Estructurados en JSON**: Cada entrada emite timestamp ISO-8601, contexto de ejecución, módulo y nivel, compatible con Datadog, ELK o Loki.
- **Pruebas de Carga con Locust**:
  ```bash
  locust -f locustfile.py --headless -u 100 -r 10 --run-time 1m -H http://localhost:8000
  ```

---

## 🧪 Pruebas y Rigor de Ingeniería (TDD)

Siguiendo el estándar universal de **Everything Claude Code (ECC)**, el desarrollo se rige por:
- **Ciclo Red → Green → Refactor**: Cobertura mínima obligatoria del **95%** configurada en `pyproject.toml` (`fail_under = 95`).
- **Inmutabilidad Absoluta**: Estructuras Pydantic congeladas para evitar efectos colaterales en la concurrencia asíncrona.
- **Seguridad Perimetral**: Validación estricta en fronteras con Schemas Pydantic y sanitización de eventos.

Ejecutar la suite completa de pruebas:
```bash
pytest --cov=src/micelio --cov-report=term-missing
```

**Métricas actuales:**
- Tests Unitarios, Integración y E2E: **79 aprobados (100%)**
- Cobertura de Código: **96.60%**

---

## 📜 Historial de Evolución Autónoma

El sistema fue desarrollado y robustecido a lo largo de un ciclo continuo de **40 iteraciones de ingeniería autónoma**:

Para consultar el registro interactivo con timeline visual y detalles de los 40 commits:
👉 **[Ver Changelog Completo en HTML](docs/changelog.html)**

---

## 💖 Apoya el Proyecto (GitHub Sponsors)

**Mycelium** es un software de código abierto (Open Source) creado para democratizar la orquestación colaborativa entre humanos e inteligencias artificiales. Cualquier persona o empresa es libre de usarlo, modificarlo y desplegarlo.

Si este proyecto te ha ahorrado tiempo, te ha servido de inspiración o lo estás utilizando para potenciar la productividad de tu organización, puedes apoyar su mantenimiento y evolución continua convirtiéndote en patrocinador:

👉 **[Patrocinar a Vicente Farías Salas en GitHub Sponsors](https://github.com/sponsors/Vicente-Farias-Salas)**

### Niveles de Reconocimiento
* **☕ Supporter ($5 / mes):** Tu nombre en la lista oficial de agradecimientos del `README.md`.
* **🚀 Enjambre Pro ($25 / mes):** Agradecimiento destacado en las notas de lanzamiento de cada versión mayor y prioridad en discusión de issues.
* **🏢 Sponsor Corporativo ($100+ / mes):** Logotipo de tu empresa en la cabecera del `README.md` y mención en el portal web del Dashboard.

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles. Puedes usarlo comercialmente, modificarlo y distribuirlo libremente.

---

<div align="center">
  <sub>Desarrollado con arquitectura de vanguardia para la era de agentes autónomos colaborativos.</sub><br>
  <sub>© 2026 Vicente Farías Salas (Mr. Mafar). Licenciado bajo MIT.</sub>
</div>
