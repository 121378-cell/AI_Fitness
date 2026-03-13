#!/usr/bin/env python3
"""Pipeline de pre-cutover: migración CSV→SQLite + quality gate."""

import argparse
import json
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
    parser = argparse.ArgumentParser(description="Run migration + quality gate pipeline")
    parser.add_argument("--output-json", help="Optional path to write pipeline summary JSON", default=None)
    args = parser.parse_args()

    summary = run_migration_and_quality_gate(TABLES, save_path=SAVE_PATH, db_path=DB_PATH)

    print(f"Pipeline passed: {summary.passed}")
    print(f"Total rows processed: {summary.total_rows_processed}")
    print(f"Validations run: {summary.quality_gate.validations_run}")

    if summary.quality_gate.failures:
        print("Failures:")
        for failure in summary.quality_gate.failures:
            print(f"- {failure}")

    if args.output_json:
        payload = {
            "passed": summary.passed,
            "total_rows_processed": summary.total_rows_processed,
            "validations_run": summary.quality_gate.validations_run,
            "failures": summary.quality_gate.failures,
            "sync_results": {k: {"name": v.name, "rows_processed": v.rows_processed} for k, v in summary.sync_results.items()},
        }
        with open(args.output_json, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        print(f"Summary JSON written to: {args.output_json}")

    return 0 if summary.passed else 1


if __name__ == "__main__":
    sys.exit(main())
