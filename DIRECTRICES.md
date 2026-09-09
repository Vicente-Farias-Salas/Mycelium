# Directrices de Desarrollo y Estándares de Proyecto — Proyecto Micelio

> **Basado en [Everything Claude Code](https://github.com/worldflowai/everything-claude-code)**  
> Estándares de producción, arquitectura modular, desarrollo guiado por pruebas (TDD), seguridad rigurosa y orquestación de agentes de IA.

---

## 1. Filosofía Central

1. **Agent-First**: Delegar tareas complejas en agentes especializados y ejecutar tareas independientes en paralelo.
2. **Plan Before Execute**: Planificar antes de modificar código con análisis de dependencias, riesgos y verificación.
3. **Test-Driven Development (TDD)**: Escribir las pruebas antes de la implementación funcional (Red → Green → Refactor). Cobertura $\ge$ 80%.
4. **Inmutabilidad Absoluta**: Nunca mutar objetos o arreglos existentes. Siempre devolver nuevas copias inmutables (`{ ...obj }`, `[ ...arr ]`).
5. **Security-First**: Cero credenciales en código duro, sanitización estricta, consultas parametrizadas y validación en límites con esquemas de tiempo de ejecución (Pydantic / Zod).

---

## 2. Reglas Críticas de Código (Coding Standards)

### 2.1 Inmutabilidad Estricta (CRÍTICO)
Nunca modifiques o mutes el estado, objetos o arreglos directamente.

### 2.2 Organización y Tamaño de Archivos
- **Límites de tamaño**: Funciones <50 líneas. Archivos típicamente 200-400 líneas (máximo absoluto 800 líneas).
- **Nivel de anidamiento**: Máximo 3 a 4 niveles. Retornos tempranos (early returns).
- **Organización por Dominio/Feature**: Agrupar código por funcionalidad o dominio de negocio.

### 2.3 Manejo Robusto de Errores
- Manejo explícito y contextualizado de excepciones; prohibidos los bloques `catch` vacíos.
- Prohibido `console.log` / `print` desestructurado en producción (usar logger configurado).
- Los mensajes al usuario no deben filtrar datos internos o stack traces.

### 2.4 Validación Estricta de Entradas (Input Validation)
- Validar siempre los datos de entrada en el límite de la aplicación usando esquemas estrictos (Pydantic en Python / Zod en TypeScript).

---

## 3. Pruebas y TDD (Testing Requirements)
- **Cobertura Mínima**: $\ge$ 80% (Unitarias, Integración y E2E).
- **Ciclo TDD Obligatorio**:
  1. **RED**: Escribir prueba primero y verificar fallo esperado.
  2. **GREEN**: Implementación mínima para que pase.
  3. **REFACTOR**: Limpiar y modularizar sin romper las pruebas.
  4. **VERIFY**: Verificar el 100% de la suite y cobertura.

---

## 4. Checklist de Seguridad Obligatorio
- [ ] Cero claves, contraseñas o tokens en código duro.
- [ ] Variables de entorno centralizadas y validadas.
- [ ] Consultas parametrizadas (sin concatenación SQL).
- [ ] Sanitización contra XSS y validación de tipos.
- [ ] Políticas CORS y CSRF adecuadas.

---

## 5. Orquestación de Agentes Especializados
- `planner`: Planificación y análisis de dependencias/riesgos.
- `architect`: Diseño de sistemas y contratos de interfaces.
- `tdd-guide`: Redacción de tests y verificación de cobertura.
- `code-reviewer`: Revisión de estilo, límites y modularidad.
- `security-reviewer`: Auditoría de vulnerabilidades y secretos.

---

## 6. Flujo de Git y Commits
- Formato **Conventional Commits**: `<tipo>: <descripción concisa>` (`feat`, `fix`, `refactor`, `test`, `docs`, `perf`, `chore`).
