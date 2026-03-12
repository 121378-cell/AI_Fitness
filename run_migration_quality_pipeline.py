#!/usr/bin/env python3
"""Pipeline de pre-cutover: migración CSV→SQLite + quality gate."""

import os
import sys
from dotenv import load_dotenv

from src.config.datasets import get_validation_tables
from src.services.pipeline_service import run_migration_and_quality_gate

load_dotenv()
SAVE_PATH = os.getenv("SAVE_PATH", os.getcwd())
DB_PATH = os.path.join(SAVE_PATH, "ai_fitness.db")

TABLES = get_validation_tables(SAVE_PATH)


def main() -> int:
    summary = run_migration_and_quality_gate(TABLES, save_path=SAVE_PATH, db_path=DB_PATH)

    print(f"Pipeline passed: {summary.passed}")
    print(f"Total rows processed: {summary.total_rows_processed}")
    print(f"Validations run: {summary.quality_gate.validations_run}")

    if summary.quality_gate.failures:
        print("Failures:")
        for failure in summary.quality_gate.failures:
            print(f"- {failure}")

    return 0 if summary.passed else 1


if __name__ == "__main__":
    sys.exit(main())
