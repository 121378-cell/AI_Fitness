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
