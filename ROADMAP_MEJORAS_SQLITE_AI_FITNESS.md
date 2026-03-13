# Roadmap de Mejoras — AI Fitness (SQLite + ETLs + Dashboard + IA)

## 1) Objetivo del roadmap

Definir una ruta **ejecutable, medible y segura** para consolidar la migración CSV→SQLite, elevar la calidad operativa en ETLs/dashboard y cerrar los pendientes detectados tras el PR de migración masiva.

Este plan prioriza:
- fiabilidad en producción,
- facilidad de mantenimiento,
- trazabilidad en CI,
- y reducción de riesgo en cutover.

---

## 2) Principios de ejecución

1. **No regresiones funcionales**: dual-write y fallback mientras no se apruebe cutover final.
2. **Cambios pequeños y verificables**: PRs de alcance acotado, con tests y criterios de aceptación.
3. **Observabilidad primero**: sin métricas/logs no hay despliegue “verde”.
4. **Documentación viva**: README + runbooks actualizados en cada fase.
5. **Compatibilidad operativa**: cron/CI deben seguir funcionando durante toda la transición.

---

## 3) Estado actual resumido

Ya existe:
- Capa `src/` con servicios de sync/validación/quality-gate/pipeline.
- Scripts operativos (`migrate_csv_to_sqlite.py`, `run_data_quality_gate.py`, `run_migration_quality_pipeline.py`).
- CI base y tests iniciales.
- Soporte multi-provider en `Gemini_Hevy.py`.

Riesgos actuales:
- cobertura de tests todavía limitada,
- documentación no totalmente alineada con configuración real,
- necesidad de endurecer evolución de esquema SQLite y observabilidad.

---

## 4) Fases del roadmap

## Fase 0 — Alineación y baseline (Semana 1)

### Objetivos
- Alinear documentación, configuración y comportamiento real.
- Definir baseline de calidad y rendimiento para medir mejoras.

### Entregables
- `.env.example` completo con IA multi-provider (`AI_PROVIDER_ORDER`, `OLLAMA_*`, `GROQ_*`, `GEMINI_*`).
- README actualizado (arquitectura actual + comandos operativos reales).
- Documento de baseline con:
  - tiempo medio pipeline,
  - filas procesadas por dataset,
  - ratio de quality gate pass/fail.

### Criterios de aceptación
- Cualquier nuevo entorno puede arrancar sin ambigüedades de configuración.
- Comandos de README reproducibles en limpio.

---

## Fase 1 — Calidad de datos y esquema SQLite (Semanas 2–3)

### Objetivos
- Robustecer capa de persistencia para producción.
- Hacer explícita la evolución de esquema.

### Entregables
- Versionado de esquema (`PRAGMA user_version`) + migraciones incrementales.
- Validaciones de esquema antes de `upsert` (columnas esperadas, tipos críticos).
- Política de manejo de columnas nuevas en CSV (adición controlada + logging).
- Índices revisados según consultas reales de dashboard.

### Criterios de aceptación
- Migraciones idempotentes.
- Sin pérdida de datos ante cambios de columnas.
- Validación automática de consistencia tras migración.

---

## Fase 2 — Testing serio (Semanas 3–4)

### Objetivos
- Subir cobertura y detectar regresiones reales.

### Entregables
- Tests unitarios ampliados para:
  - `database.py` (coerción, fechas, upsert, índices),
  - `validation_service.py`,
  - `quality_gate_service.py`.
- Tests de integración con fixtures CSV+SQLite temporales.
- Tests de CLI para exit codes y JSON output.
- Objetivo inicial de cobertura: **>=70% en `src/`**.

### Criterios de aceptación
- Pipeline CI falla ante regresión de datos, no solo ante errores sintácticos.
- Cobertura visible en CI y tendencia ascendente.

---

## Fase 3 — Observabilidad y operación (Semanas 4–5)

### Objetivos
- Tener diagnóstico rápido de fallos en cron/CI/servidor.

### Entregables
- Logging estructurado JSON en servicios críticos.
- `run_id` por ejecución para correlación entre sync, quality gate y pipeline.
- Artefactos de salida ampliados:
  - tiempos por etapa,
  - filas leídas/escritas/omitidas,
  - lista de warnings operativos.
- Runbook de incidentes (DB lock, CSV faltante, schema drift, fallo proveedor IA).

### Criterios de aceptación
- Cada ejecución permite identificar causa raíz en <10 minutos.
- Métricas mínimas disponibles en CI y local.

---

## Fase 4 — Refactor controlado de componentes críticos (Semanas 5–7)

### Objetivos
- Reducir deuda técnica en archivos monolíticos.

### Entregables
- Modularización de `Gemini_Hevy.py`:
  - `ai/providers.py`
  - `ai/orchestrator.py`
  - `ai/prompt_context.py`
  - `hevy/client.py`
- Separación progresiva de lógica de datos/UI del dashboard en módulos reutilizables.
- Contratos internos (interfaces simples) para facilitar testeo.

### Criterios de aceptación
- Misma funcionalidad, menor complejidad ciclomática.
- Nuevos módulos con tests propios.

---

## Fase 5 — Endurecimiento CI/CD (Semanas 7–8)

### Objetivos
- Convertir CI en compuerta de calidad efectiva.

### Entregables
- Lint + formato + tipado (`ruff`, `mypy` sobre `src/` inicialmente).
- Matrix de Python soportadas.
- Jobs separados: unit, integration, pipeline smoke, docs-check.
- Política de merge: sin verde en gates críticos no hay merge.

### Criterios de aceptación
- Reducción de bugs post-merge.
- Tiempo de CI dentro de objetivo (p.ej. <10 min en PR estándar).

---

## Fase 6 — Cutover gradual y estabilización (Semanas 9–10)

### Objetivos
- Pasar consumidores principales a SQLite con control de riesgo.

### Entregables
- Plan de cutover por componente (ETLs, dashboard, reportes).
- Ventana de convivencia CSV+SQLite con validación automática diaria.
- Checklist de rollback documentado y probado.

### Criterios de aceptación
- 2 semanas sin discrepancias críticas en quality gate.
- Dashboard y ETLs estables bajo carga habitual.

---

## 5) Backlog priorizado (Top 15)

1. Crear `.env.example` definitivo y validación central de config.
2. Actualizar README con arquitectura actual y fallback IA.
3. Añadir migraciones versionadas de SQLite.
4. Añadir tests de integración de sync/upsert.
5. Añadir tests CLI (`quality`/`pipeline`).
6. Incluir cobertura en CI.
7. Logging JSON + `run_id`.
8. Artefacto JSON ampliado con timings.
9. Runbook operativo de incidencias.
10. Refactor inicial de `Gemini_Hevy.py` por módulos.
11. Tipado incremental en `src/services`.
12. `ruff` y reglas mínimas de estilo.
13. `mypy` parcial (strict por módulos nuevos).
14. Pipeline smoke en datos de fixture.
15. Checklist final de cutover y rollback.

---

## 6) Matriz de riesgos y mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigación |
|---|---:|---:|---|
| Drift CSV↔SQLite por cambios de columnas | Alto | Medio | validación de esquema + quality gate diario |
| Bloqueos SQLite en cron concurrente | Medio | Medio | WAL + busy_timeout + escalonado de cron + retries |
| Falso “verde” en CI por tests superficiales | Alto | Alto | integración con fixtures y cobertura mínima |
| Rotura por refactor grande del dashboard | Alto | Medio | refactor por etapas + snapshot tests |
| Fallo proveedor IA principal | Medio | Alto | fallback ordenado + alertas + documentación de operación |

---

## 7) KPIs de seguimiento

- **Calidad de datos**
  - % ejecuciones quality gate en verde.
  - nº discrepancias por tabla/semana.
- **Fiabilidad operativa**
  - tasa de éxito de cron ETLs.
  - MTTR de incidencias de datos.
- **Calidad de ingeniería**
  - cobertura total y por paquete.
  - defectos post-merge.
- **Rendimiento**
  - tiempo total del pipeline.
  - latencia de consultas del dashboard.

Objetivos iniciales (90 días):
- >98% ejecuciones quality gate en verde,
- cobertura `src/` >75%,
- 0 pérdidas de datos en migraciones,
- reducción de incidentes operativos >50%.

---

## 8) Cadencia de trabajo recomendada

- **Semanal**: planning + revisión de KPIs + riesgos.
- **Por PR**: checklist de calidad (tests, docs, rollback, observabilidad).
- **Quincenal**: demo técnica y ajuste de prioridades.

---

## 9) Definición de “Done” por mejora

Una mejora se considera terminada cuando:
1. Está implementada con tests relevantes.
2. Tiene documentación actualizada.
3. Se observa en logs/artefactos si aplica.
4. Pasa CI completo.
5. Tiene plan de rollback (si toca runtime crítico).

---

## 10) Siguiente PR recomendado (rápido y de alto impacto)

**PR-1 (alcance corto, 1–2 días):**
- README + `.env.example` alineados con estado real.
- validación central de configuración.
- 3–5 tests nuevos de integración básica.

Resultado esperado: reducir ambigüedad operativa y bloquear errores de configuración antes de runtime.
