# Migración segura de CSV a SQLite (AI Fitness)

## 1) Preparar un branch aislado

```bash
git checkout -b feat/sqlite-migration
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2) Ejecutar migración sin borrar CSV

```bash
python migrate_csv_to_sqlite.py
```

Este script:
- Lee los CSV actuales (`garmin_stats.csv`, `garmin_activities.csv`, `garmin_runs.csv`).
- Inserta/actualiza en `ai_fitness.db`.
- **No elimina ni altera** los CSV de origen.

## 3) Validar tabla por tabla

```bash
python sqlite_validation_examples.py
```

Valida para cada tabla:
- Conteo de filas CSV vs SQLite.
- Coincidencia de fechas.
- Preservación de valores clave.

## 4) Probar ETLs y dashboard antes de reemplazar CSV

### ETLs diarios/históricos
Ejecuta una muestra real:

```bash
python daily_garmin_health.py
python daily_garmin_activities.py
python history_garmin_import.py --backfill
```

Cada script sigue escribiendo CSV (compatibilidad) y además sincroniza SQLite.

### Dashboard

```bash
streamlit run dashboard_local_server.py
```

El dashboard ahora intenta leer SQLite primero y usa CSV como fallback.

## 5) Commits frecuentes recomendados

Sugerencia de granularidad:

```bash
git add src/database.py migrate_csv_to_sqlite.py

git commit -m "feat(db): add sqlite access layer and migration script"

git add daily_*.py history_*.py update_yesterday_garmin.py

git commit -m "feat(etl): sync csv pipelines to sqlite"

git add dashboard_local_server.py sqlite_validation_examples.py MIGRACION_SQLITE.md

git commit -m "feat(dashboard): load data from sqlite with csv fallback"
```

## 6) Seguridad, concurrencia y anti-corrupción

En `src/database.py` se implementa:

- `with sqlite3.connect(...) as conn` para transacciones atómicas y cierre seguro.
- `PRAGMA journal_mode=WAL` para mejorar concurrencia (lectores + escritor simultáneos).
- `PRAGMA busy_timeout` para esperar lock y reducir errores de contención.
- UPSERT con `ON CONFLICT` para evitar duplicados y preservar idempotencia.

Buenas prácticas adicionales:
- Mantener escrituras cortas y en lotes (`executemany`).
- Evitar transacciones largas en procesos cron concurrentes.
- Si hay mucha simultaneidad, escalonar cron (ej. minuto 30, 35, 40 como ya está).

## 7) Cutover gradual (sin riesgo)

1. Mantén ambos formatos activos 1-2 semanas (CSV + SQLite).
2. Monitorea validación periódica con `sqlite_validation_examples.py`.
3. Cuando no haya diferencias, cambia consumidores secundarios a SQLite.
4. Recién al final, decide archivar CSV (no borrar sin backup).


## 8) Mejoras de fase 2 (persistencia robusta)

- La capa SQLite ahora crea columnas con afinidad de tipo (`INTEGER`, `REAL`, `TEXT`) según el nombre de columna.
- Se crean índices recomendados por tabla para acelerar dashboard y validaciones.
- La migración usa sincronización global (`sync_all_configured_csv`) para evitar drift entre tablas configuradas.
- Las validaciones incluyen chequeo de duplicados por PK lógica en SQLite.



## 9) Siguiente tarea del plan: capa de servicios de sincronización

- Se agregó `src/services/sync_service.py` para desacoplar la orquestación de sincronización del script de migración y de ETLs.
- `migrate_csv_to_sqlite.py` ahora consume `sync_all_datasets()` y reporta resultados tipados por dataset.
- ETLs pueden migrar progresivamente desde llamadas directas a DB (`sync_csv_to_table`) hacia servicios (`sync_single_dataset`) sin romper comportamiento actual.



## 10) Siguiente tarea del plan: ETLs consumen la capa de servicios

- Se migraron los scripts ETL e históricos restantes para usar `sync_single_dataset(...)` desde `src/services/sync_service.py`.
- Esto reduce el acoplamiento directo de los scripts contra funciones internas de `src/database.py`.
- El comportamiento funcional se mantiene: cada script sigue escribiendo CSV y luego sincroniza SQLite (dual-write de transición).



## 11) Siguiente tarea del plan: logging estructurado en servicios

- Se agregó `src/logging_utils.py` para centralizar logger con formato homogéneo.
- `src/services/sync_service.py` ahora emite logs de inicio/fin por dataset y sincronización global.
- `migrate_csv_to_sqlite.py` usa logger estructurado para mejorar trazabilidad operativa y facilitar debug en cron/CI.



## 12) Siguiente tarea del plan: servicio de validación reutilizable

- Se agregó `src/services/validation_service.py` para encapsular validaciones CSV vs SQLite (filas, fechas, duplicados por PK lógica y valores faltantes por columna).
- `sqlite_validation_examples.py` ahora consume este servicio, evitando duplicación de lógica de validación y preparando la base para checks automáticos en CI.
- Esta tarea mantiene el enfoque no destructivo: sólo valida consistencia entre orígenes, no altera ni elimina CSV.



## 13) Siguiente tarea del plan: quality gate automatizable

- Se agregó `src/services/quality_gate_service.py` para ejecutar una compuerta de calidad reutilizable basada en las validaciones CSV vs SQLite.
- Se añadió `run_data_quality_gate.py` como entrypoint para automatizar en local/CI (exit code 0/1 según pase o falle).
- Si no existen ni CSV ni DB en un entorno limpio, el quality gate se marca como ejecución vacía exitosa para no bloquear CI por falta de fixtures.
- Esto permite integrar controles de paridad como paso previo al cutover definitivo a SQLite.



## 14) Siguiente tarea del plan: pipeline pre-cutover unificado

- Se agregó `src/services/pipeline_service.py` para ejecutar en un solo flujo: sincronización CSV→SQLite + quality gate.
- Se añadió `run_migration_quality_pipeline.py` como entrypoint único para pre-cutover (útil en CI/cron técnico).
- El pipeline devuelve exit code `0/1` y resume filas procesadas + estado de validaciones para facilitar automatización y observabilidad.



## 15) Siguiente tarea del plan: configuración única de datasets

- Se agregó `src/config/datasets.py` para centralizar la definición de tablas usadas por validación y quality gates.
- `sqlite_validation_examples.py`, `run_data_quality_gate.py` y `run_migration_quality_pipeline.py` ahora consumen `get_validation_tables(...)`.
- Esto elimina duplicación de configuración y reduce riesgo de drift entre entrypoints operativos.



## 16) Cierre de tareas pendientes del plan (automatización completa)

- Se agregó workflow de CI en `.github/workflows/sqlite-migration-checks.yml` para ejecutar compilación y pipeline pre-cutover automáticamente en push/PR.
- Se añadió `Makefile` con comandos operativos estándar (`migrate`, `validate`, `quality`, `pipeline`, `ci-check`) para facilitar ejecución local y runbooks.
- Con esto queda cubierta la automatización base del plan: migración, validación, quality gate y pipeline unificado en local/CI.



## 17) Siguiente tarea del plan: artefactos JSON para CI/observabilidad

- `run_data_quality_gate.py` y `run_migration_quality_pipeline.py` ahora aceptan `--output-json` para exportar resultados estructurados.
- El workflow CI sube `pipeline_summary.json` como artifact (`sqlite-pipeline-summary`) para auditoría y trazabilidad.
- El `Makefile` añade `quality-json` y `pipeline-json` para generar estos artefactos localmente.



## 18) Siguiente tarea del plan: tests de servicios base

- Se añadió `tests/test_services.py` con pruebas unitarias sobre configuración compartida, quality gate y propiedades de `PipelineSummary`.
- El workflow CI ahora ejecuta `python -m unittest -v tests.test_services` antes de compilación/pipeline.
- El `Makefile` agrega `test-services` y `ci-check` ahora también corre este bloque de pruebas.

