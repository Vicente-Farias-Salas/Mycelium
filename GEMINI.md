# Workspace Guidelines (Antigravity) — Proyecto Micelio

Este proyecto sigue rigurosamente las directrices de ingeniería de software y orquestación de agentes basadas en [Everything Claude Code](https://github.com/worldflowai/everything-claude-code).

Consulta el documento maestro de directrices en: [DIRECTRICES.md](file:///c:/Users/user/Documents/PROYECTOS/proyecto%20micelio/DIRECTRICES.md).

## Reglas Críticas Inmediatas:
1. **Inmutabilidad Absoluta**: Nunca mutar objetos o arrays. Retornar siempre nuevas copias estructuradas (`{ ...obj }`, `[ ...arr ]`).
2. **Archivos Pequeños y Modulares**: Funciones <50 líneas, archivos de 200-400 líneas (máximo absoluto 800 líneas).
3. **Manejo de Errores y Validación**: Validar entradas en límites (Pydantic / Zod) y capturar excepciones contextualmente. Cero `console.log` / prints desestructurados en producción.
4. **TDD Obligatorio**: Red → Green → Refactor. Cobertura mínima del 80% (unit, integration, E2E).
5. **Seguridad Estricta**: Cero secretos en código, variables de entorno validadas, consultas parametrizadas, sanitización de entradas y salidas.
6. **Orquestación de Agentes**: Usar roles especializados (`planner`, `architect`, `tdd-guide`, `code-reviewer`, `security-reviewer`, `build-error-resolver`) y ejecutar en paralelo tareas independientes.
7. **Filosofía Ponytail**: Solución más simple y directa, usar stdlib antes que dependencias pesadas, YAGNI.
8. **Git**: Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, etc.).
