# 🍄 Mycelium — Enterprise Agent-to-Agent (A2A) Collaborative SaaS

> Plataforma B2B para organizaciones donde los agentes personales de IA cohabitan una **Oficina Virtual en Tiempo Real** sobre un sustrato vivo compartido, eliminando la dispersión documental y el traspaso manual de información.

---

## 🌟 Concepto Central

En las organizaciones tradicionales, el flujo de trabajo entre humanos y sus IAs sufre de **inflación y dispersión documental**:
- Un directivo genera un documento de 50 páginas con su IA.
- El colaborador lo limpia y comprime a 10 páginas con su IA.
- El directivo le pide a su IA que se lo resuma a 3 viñetas.
- El humano actúa como un simple intermediario manual de copiar y pegar.

**Proyecto Micelio** transforma esta dinámica mediante una **Oficina Virtual de Agentes (A2A Living Substrate)**:
1. **Concepción Asistida**: El directivo y su agente formulan el proyecto; el agente genera la síntesis y pregunta: *"¿A quién enviamos el proyecto o calculo los más óptimos?"*.
2. **Optimización Multivariable de Equipos (`TeamOptimizer`)**: Analiza las capacidades de los agentes, los departamentos y la carga laboral para recomendar el equipo ideal.
3. **Solicitudes de Unión Interdepartamentales**: Notifica y enrola tanto al colaborador humano como a su agente.
4. **Bootstrapping Automatizado del Workspace**: Al unirse, el agente del colaborador crea la carpeta física local del proyecto y redacta el informe tripartito:
   - 📥 **¿Qué llegó?** (Alcance, specs y contratos).
   - 🛠️ **¿Qué se ha hecho?** (Historial y decisiones previas).
   - 🚀 **¿Qué podemos hacer?** (Plan de acción inmediato).
5. **Sustrato Vivo en Tiempo Real (No Collage)**: Los agentes intercambian eventos de contrato, consultas y consenso en el canal de la oficina (`SynapseBus`), evitando colisiones y entregando un resultado coherente.

---

## 🏗️ Arquitectura del Sistema

```
                        ┌──────────────────────────────────────────────┐
                        │        OFICINA VIRTUAL (SUSTRATO VIVO)       │
                        │                                              │
[ Agente Jefe ] ◄───────┼──► [ Bus de Sinapsis (A2A Real-time) ] ◄────┼───► [ Agente Colaborador ]
(Concepción & Matching) │    • STATE_MUTATION                          │    (Bootstrapping & Briefing)
                        │    • AGENT_QUERY                             │
                        │    • AGENT_CONSENSUS                         │
                        └──────────────────────────────────────────────┘
                                                │
                                                ▼
                                    [ Directorio Local ]
                                    • README.md
                                    • briefing.md (¿Qué llegó / Qué se hizo / Qué hacer?)
```

---

## 🚀 Instalación y Uso Rápido

```bash
# Crear entorno virtual e instalar dependencias
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install -e .

# Ejecutar el servidor
python src/micelio/main.py
```

El servidor quedará disponible en `http://localhost:8000` con documentación OpenAPI en `http://localhost:8000/docs`.

---

## 🧪 Pruebas y Cobertura (TDD)

El proyecto sigue estrictamente el ciclo **Red → Green → Refactor** bajo el estándar [Everything Claude Code (ECC)](https://github.com/worldflowai/everything-claude-code):

```bash
.\.venv\Scripts\python.exe -m pytest --cov=src/micelio --cov-report=term-missing tests/
```

- **Cobertura actual**: **93.21%** (20 pruebas pasando: Unitarias, Integración y E2E).
- **Inmutabilidad estricta**: Modelos Pydantic v2 congelados (`frozen=True`).
- **Seguridad**: Prevención de Path Traversal y validación de esquemas en tiempo de ejecución.
