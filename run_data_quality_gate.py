#!/usr/bin/env python3
"""Ejecuta una compuerta de calidad CSV vs SQLite para automatización local/CI."""

import argparse
import json
import os
import sys
from dotenv import load_dotenv

from src.config.datasets import get_validation_tables
from src.services.quality_gate_service import run_quality_gate

load_dotenv()
SAVE_PATH = os.getenv("SAVE_PATH", os.getcwd())
DB_PATH = os.path.join(SAVE_PATH, "ai_fitness.db")

TABLES = get_validation_tables(SAVE_PATH)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CSV↔SQLite quality gate")
    parser.add_argument("--output-json", help="Optional path to write summary JSON", default=None)
    args = parser.parse_args()

    summary = run_quality_gate(TABLES, save_path=SAVE_PATH, db_path=DB_PATH)

    print(f"Quality gate passed: {summary.passed}")
    print(f"Validations run: {summary.validations_run}")
    if summary.failures:
        print("Failures:")
        for failure in summary.failures:
            print(f"- {failure}")

    if args.output_json:
        payload = {
            "passed": summary.passed,
            "validations_run": summary.validations_run,
            "failures": summary.failures,
        }
        with open(args.output_json, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        print(f"Summary JSON written to: {args.output_json}")

    return 0 if summary.passed else 1


if __name__ == "__main__":
    sys.exit(main())
