# AI Fitness Dashboard

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)

Dashboard personal de fitness centrado en **Garmin** con almacenamiento híbrido **SQLite + CSV fallback**.

## Características

- Sincronización de salud y actividad desde Garmin.
- Dashboard Streamlit con tendencias de salud y actividad reciente.
- Pipeline de migración CSV→SQLite y quality gate pre-cutover.
- Tooling de operación (`Makefile`, scripts y CI).

## Quick Start

```bash
git clone https://github.com/johnson4601/AI_Fitness.git
cd AI_Fitness
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
python3 setup.py
streamlit run dashboard_local_server.py
```

## Configuración (.env)

```ini
SAVE_PATH=/path/to/AI_Fitness_Data
DRIVE_MOUNT_PATH=/path/to/GDrive
GARMIN_EMAIL=your_email@example.com
GARMIN_PASSWORD=your_password
CHECK_MOUNT_STATUS=False
DASHBOARD_PORT=8501
AI_FITNESS_LOG_LEVEL=INFO
```

También puedes copiar y ajustar `.env.example`.

## Operación de migración/calidad

```bash
make migrate
make validate
make quality
make pipeline
make ci-check
```

## Estructura relevante

- `daily_garmin_health.py`
- `daily_garmin_activities.py`
- `daily_garmin_runs.py`
- `history_garmin_import.py`
- `history_garmin_activities.py`
- `history_garmin_runs.py`
- `src/database.py`
- `src/services/*`
- `run_migration_quality_pipeline.py`

## Nota

Este repositorio está alineado a alcance Garmin-only.
