#!/usr/bin/env python3
"""Ejecuta una compuerta de calidad CSV vs SQLite para automatización local/CI."""

import os
import sys
from typing import Dict

from dotenv import load_dotenv

from src.services.quality_gate_service import run_quality_gate

load_dotenv()
SAVE_PATH = os.getenv("SAVE_PATH", os.getcwd())
DB_PATH = os.path.join(SAVE_PATH, "ai_fitness.db")

TABLES: Dict[str, Dict[str, object]] = {
    "garmin_stats": {
        "csv": os.path.join(SAVE_PATH, "garmin_stats.csv"),
        "date_col": "Date",
        "check_cols": ["Weight (lbs)", "RHR", "Steps"],
    },
    "hevy_stats": {
        "csv": os.path.join(SAVE_PATH, "hevy_stats.csv"),
        "date_col": "Date",
        "check_cols": ["Workout", "Exercise", "Weight (lbs)", "Reps"],
    },
    "garmin_activities": {
        "csv": os.path.join(SAVE_PATH, "garmin_activities.csv"),
        "date_col": "Date",
        "check_cols": ["activityName", "sportType", "distance"],
    },
    "garmin_runs": {
        "csv": os.path.join(SAVE_PATH, "garmin_runs.csv"),
        "date_col": "Date",
        "check_cols": ["activityName", "averageSpeed", "averageHR"],
    },
}


def main() -> int:
    summary = run_quality_gate(TABLES, save_path=SAVE_PATH, db_path=DB_PATH)

    print(f"Quality gate passed: {summary.passed}")
    print(f"Validations run: {summary.validations_run}")
    if summary.failures:
        print("Failures:")
        for failure in summary.failures:
            print(f"- {failure}")

    return 0 if summary.passed else 1


if __name__ == "__main__":
    sys.exit(main())
