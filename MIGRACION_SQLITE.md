# Migración segura de CSV a SQLite (AI Fitness Garmin-only)

## 1) Objetivo

Migrar los datasets de Garmin a SQLite sin destruir CSV y con validación previa al cutover.

## 2) Datasets incluidos

- `garmin_stats.csv`
- `garmin_activities.csv`
- `garmin_runs.csv`

## 3) Flujo recomendado

```bash
python migrate_csv_to_sqlite.py
python sqlite_validation_examples.py
AI_FITNESS_LOG_LEVEL=INFO python run_migration_quality_pipeline.py --output-json pipeline_summary.json
```

## 4) Buenas prácticas

- Mantener dual-write durante transición.
- Ejecutar quality gate diariamente.
- No retirar CSV hasta tener ventana estable sin discrepancias.

## 5) Comandos Makefile

```bash
make migrate
make validate
make quality
make pipeline
make ci-check
```


## 6) Versionado de esquema

La capa `src/database.py` aplica migraciones incrementales automáticas usando `PRAGMA user_version`
al abrir conexión/transacción.

- Versión actual: `1`
- Migración v1: agrega columna `ingested_at` a tablas Garmin existentes si no existe.


## 7) Validaciones pre-upsert

Antes de insertar, `src/database.py` valida:
- columnas PK requeridas,
- columnas de fecha requeridas,
- consistencia longitud fila/header,
- compatibilidad con columnas existentes cuando la tabla ya existe.

Si aparecen columnas nuevas no migradas, el upsert falla explícitamente para evitar drift silencioso.
