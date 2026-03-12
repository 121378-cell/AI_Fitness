#!/usr/bin/env python3
"""Ejemplos de validación CSV vs SQLite por tabla migrada."""

import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
SAVE_PATH = os.getenv("SAVE_PATH", os.getcwd())
DB_PATH = os.path.join(SAVE_PATH, "ai_fitness.db")

TABLES = {
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


def norm_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", format="mixed").dt.strftime("%Y-%m-%d")


def validate_table(conn: sqlite3.Connection, table: str, cfg: dict) -> None:
    csv_path = cfg["csv"]
    if not os.path.exists(csv_path):
        print(f"[WARN] {table}: CSV no existe ({csv_path}), se omite.")
        return

    df_csv = pd.read_csv(csv_path)
    df_sql = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)

    print(f"\n=== {table} ===")
    print(f"CSV rows: {len(df_csv)} | SQLite rows: {len(df_sql)}")

    if len(df_csv) != len(df_sql):
        print("[FAIL] Conteo de filas no coincide")
    else:
        print("[OK] Conteo de filas coincide")

    date_col = cfg["date_col"]
    if date_col in df_csv.columns and date_col in df_sql.columns:
        csv_dates = set(norm_date(df_csv[date_col]).dropna())
        sql_dates = set(norm_date(df_sql[date_col]).dropna())
        if csv_dates == sql_dates:
            print("[OK] Fechas coinciden")
        else:
            print(f"[FAIL] Fechas diferentes. Solo CSV: {len(csv_dates - sql_dates)}, Solo SQL: {len(sql_dates - csv_dates)}")

    for col in cfg["check_cols"]:
        if col not in df_csv.columns or col not in df_sql.columns:
            print(f"[WARN] Columna {col} no está en ambos orígenes")
            continue

        csv_vals = set(df_csv[col].dropna().astype(str))
        sql_vals = set(df_sql[col].dropna().astype(str))
        if csv_vals.issubset(sql_vals):
            print(f"[OK] Valores preservados para columna: {col}")
        else:
            diff = list(csv_vals - sql_vals)[:5]
            print(f"[FAIL] Valores faltantes en SQLite para {col}. Muestra: {diff}")


if __name__ == "__main__":
    with sqlite3.connect(DB_PATH) as conn:
        for table_name, table_cfg in TABLES.items():
            validate_table(conn, table_name, table_cfg)
