import os
import sqlite3
from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from src.logging_utils import get_logger
from src.services.validation_service import ValidationResult, validate_table_pair

logger = get_logger("ai_fitness.quality_gate")


@dataclass
class QualityGateSummary:
    passed: bool
    validations_run: int
    failures: List[str]


def run_quality_gate(tables: Dict[str, Dict[str, object]], save_path: str, db_path: str) -> QualityGateSummary:
    failures: List[str] = []
    validations_run = 0

    if not os.path.exists(db_path):
        has_any_csv = any(os.path.exists(cfg["csv"]) for cfg in tables.values())
        msg = f"Base SQLite no encontrada: {db_path}"
        if has_any_csv:
            logger.error(msg)
            return QualityGateSummary(passed=False, validations_run=0, failures=[msg])
        logger.warning("%s (sin CSV disponibles, se considera ejecución vacía)", msg)
        return QualityGateSummary(passed=True, validations_run=0, failures=[])

    with sqlite3.connect(db_path) as conn:
        for table_name, cfg in tables.items():
            csv_path = cfg["csv"]
            if not os.path.exists(csv_path):
                logger.warning("CSV ausente para %s: %s (se omite)", table_name, csv_path)
                continue

            df_csv = pd.read_csv(csv_path)
            df_sql = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)

            result: ValidationResult = validate_table_pair(
                table_name=table_name,
                df_csv=df_csv,
                df_sql=df_sql,
                date_col=cfg.get("date_col"),
                check_cols=cfg.get("check_cols", []),
            )
            validations_run += 1

            if not result.row_count_match:
                failures.append(f"{table_name}: row_count_mismatch")
            if result.date_set_match is False:
                failures.append(f"{table_name}: date_set_mismatch")
            if result.pk_duplicates > 0:
                failures.append(f"{table_name}: pk_duplicates={result.pk_duplicates}")
            if result.missing_values_by_column:
                failures.append(f"{table_name}: missing_values={list(result.missing_values_by_column.keys())}")

    passed = len(failures) == 0
    logger.info("Quality gate finished (passed=%s, validations_run=%s, failures=%s)", passed, validations_run, len(failures))
    return QualityGateSummary(passed=passed, validations_run=validations_run, failures=failures)
