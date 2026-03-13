# AI Fitness Dashboard

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)

Personal fitness command center focused on **Garmin** data pipelines, SQLite migration quality checks, and dashboard visualization.

## Scope update

> This repository is Garmin-only for data ingestion and analytics.

## Features

- Garmin health sync (`garmin_stats.csv`)
- Garmin activities sync (`garmin_activities.csv`, `garmin_runs.csv`)
- SQLite migration pipeline with quality gate
- Streamlit dashboard (Garmin-only)
- Centralized AI provider config utilities

## Quick start

```bash
git clone https://github.com/johnson4601/AI_Fitness.git
cd AI_Fitness
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python setup.py
```

Run dashboard:

```bash
streamlit run dashboard_local_server.py
```

## Environment variables

Use `.env.example` as template.

Key groups:
- Paths: `SAVE_PATH`, `DRIVE_MOUNT_PATH`
- Garmin: `GARMIN_EMAIL`, `GARMIN_PASSWORD`
- AI providers: `AI_PROVIDER_ORDER`, `OLLAMA_*`, `GROQ_*`, `GEMINI_*`
- System: `CHECK_MOUNT_STATUS`, `PROJECT_DIR`, `LOG_FILE`, `DASHBOARD_PORT`

## Migration & quality commands

```bash
make migrate
make validate
make quality
make pipeline
make ci-check
```

## Garmin cron example

```bash
30 * * * * cd /home/pi/Documents/AI_Fitness && /usr/bin/python3 daily_garmin_health.py >> /home/pi/cron_log.txt 2>&1
40 * * * * cd /home/pi/Documents/AI_Fitness && /usr/bin/python3 daily_garmin_activities.py >> /home/pi/cron_log.txt 2>&1
0 6 * * * cd /home/pi/Documents/AI_Fitness && /usr/bin/python3 update_yesterday_garmin.py >> /home/pi/cron_log.txt 2>&1
```

## License

MIT
