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
- Lee los CSV actuales (`garmin_stats.csv`, `hevy_stats.csv`, `garmin_activities.csv`, `garmin_runs.csv`).
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
python daily_hevy_workouts.py
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

