#!/usr/bin/env python3
"""Ejemplos de validación CSV vs SQLite por tabla migrada."""

import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv

from src.config.datasets import get_validation_tables
from src.services.validation_service import validate_table_pair

load_dotenv()
SAVE_PATH = os.getenv("SAVE_PATH", os.getcwd())
DB_PATH = os.path.join(SAVE_PATH, "ai_fitness.db")

TABLES = get_validation_tables(SAVE_PATH)


def validate_table(conn: sqlite3.Connection, table: str, cfg: dict) -> None:
    csv_path = cfg["csv"]
    if not os.path.exists(csv_path):
        print(f"[WARN] {table}: CSV no existe ({csv_path}), se omite.")
        return

    df_csv = pd.read_csv(csv_path)
    df_sql = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)

    result = validate_table_pair(
        table_name=table,
        df_csv=df_csv,
        df_sql=df_sql,
        date_col=cfg.get("date_col"),
        check_cols=cfg.get("check_cols", []),
    )

    print(f"\n=== {table} ===")
    print(f"CSV rows: {len(df_csv)} | SQLite rows: {len(df_sql)}")

    print("[OK] Conteo de filas coincide" if result.row_count_match else "[FAIL] Conteo de filas no coincide")

    if result.date_set_match is not None:
        print("[OK] Fechas coinciden" if result.date_set_match else "[FAIL] Fechas no coinciden")

    if result.pk_duplicates == 0:
        print("[OK] Sin duplicados por PK lógica")
    else:
        print(f"[FAIL] Se detectaron {result.pk_duplicates} duplicados por PK lógica")

    if not result.missing_values_by_column:
        print("[OK] Valores clave preservados")
    else:
        for col, sample in result.missing_values_by_column.items():
            print(f"[FAIL] Valores faltantes en SQLite para {col}. Muestra: {sample}")


if __name__ == "__main__":
    with sqlite3.connect(DB_PATH) as conn:
        for table_name, table_cfg in TABLES.items():
            validate_table(conn, table_name, table_cfg)
