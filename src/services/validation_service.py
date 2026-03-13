from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd

from src.database import TABLE_CONFIG
from src.logging_utils import get_logger

logger = get_logger("ai_fitness.validation_service")


@dataclass
class ValidationResult:
    table: str
    row_count_match: bool
    date_set_match: Optional[bool]
    pk_duplicates: int
    missing_values_by_column: Dict[str, List[str]]


def _norm_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", format="mixed").dt.strftime("%Y-%m-%d")


def validate_table_pair(
    table_name: str,
    df_csv: pd.DataFrame,
    df_sql: pd.DataFrame,
    date_col: Optional[str],
    check_cols: List[str],
) -> ValidationResult:
    logger.info("Validating table pair for %s", table_name)

    row_count_match = len(df_csv) == len(df_sql)

    date_set_match: Optional[bool] = None
    if date_col and date_col in df_csv.columns and date_col in df_sql.columns:
        csv_dates = set(_norm_date(df_csv[date_col]).dropna())
        sql_dates = set(_norm_date(df_sql[date_col]).dropna())
        date_set_match = csv_dates == sql_dates

    pk_cols = TABLE_CONFIG.get(table_name, {}).get("pk", [])
    pk_duplicates = 0
    if pk_cols and all(col in df_sql.columns for col in pk_cols):
        pk_duplicates = int(df_sql.duplicated(subset=pk_cols).sum())

    missing_values_by_column: Dict[str, List[str]] = {}
    for col in check_cols:
        if col not in df_csv.columns or col not in df_sql.columns:
            continue
        csv_vals = set(df_csv[col].dropna().astype(str))
        sql_vals = set(df_sql[col].dropna().astype(str))
        missing = list(csv_vals - sql_vals)
        if missing:
            missing_values_by_column[col] = missing[:5]

    result = ValidationResult(
        table=table_name,
        row_count_match=row_count_match,
        date_set_match=date_set_match,
        pk_duplicates=pk_duplicates,
        missing_values_by_column=missing_values_by_column,
    )
    logger.info(
        "Validation complete for %s (rows_match=%s, date_match=%s, pk_dup=%s)",
        table_name,
        result.row_count_match,
        result.date_set_match,
        result.pk_duplicates,
    )
    return result
