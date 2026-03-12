import csv
import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from dotenv import load_dotenv

load_dotenv()


def get_db_path(db_path: Optional[str] = None) -> str:
    if db_path:
        return db_path
    save_path = os.getenv("SAVE_PATH", os.getcwd())
    return os.path.join(save_path, "ai_fitness.db")


TABLE_CONFIG: Dict[str, Dict[str, Any]] = {
    "garmin_stats": {"csv": "garmin_stats.csv", "pk": ["Date"], "date_cols": ["Date"]},
    "hevy_stats": {
        "csv": "hevy_stats.csv",
        "pk": ["Date", "Workout", "Exercise", "Set"],
        "date_cols": ["Date"],
    },
    "garmin_activities": {"csv": "garmin_activities.csv", "pk": ["activityId"], "date_cols": ["Date"]},
    "garmin_runs": {
        "csv": "garmin_runs.csv",
        "pk": ["Date", "Time", "activityName"],
        "date_cols": ["Date"],
    },
}


def _quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _normalize_date(value: Any) -> Any:
    if value in (None, ""):
        return None
    text = str(value).strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
        return text
    try:
        return datetime.strptime(text, "%m/%d/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return text


def _coerce_value(value: Any) -> Any:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    if re.match(r"^-?\d+$", text):
        try:
            return int(text)
        except ValueError:
            pass
    if re.match(r"^-?\d*\.\d+$", text):
        try:
            return float(text)
        except ValueError:
            pass
    return text


def connect_db(db_path: Optional[str] = None, timeout: float = 30.0) -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path(db_path), timeout=timeout)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def close_db(conn: sqlite3.Connection) -> None:
    conn.close()


@contextmanager
def transaction(db_path: Optional[str] = None) -> Iterable[sqlite3.Connection]:
    with sqlite3.connect(get_db_path(db_path), timeout=30.0) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 5000")
        yield conn


def execute_query(query: str, params: Iterable[Any] = (), db_path: Optional[str] = None) -> None:
    with transaction(db_path) as conn:
        conn.execute(query, tuple(params))


def fetch_all(query: str, params: Iterable[Any] = (), db_path: Optional[str] = None) -> List[sqlite3.Row]:
    with transaction(db_path) as conn:
        cursor = conn.execute(query, tuple(params))
        return cursor.fetchall()


def ensure_table(
    table_name: str,
    headers: List[str],
    primary_keys: Optional[List[str]] = None,
    db_path: Optional[str] = None,
) -> None:
    if not headers:
        return
    column_defs = ", ".join([f"{_quote(col)} TEXT" for col in headers])
    pk_clause = ""
    if primary_keys:
        pk_cols = ", ".join([_quote(col) for col in primary_keys])
        pk_clause = f", PRIMARY KEY ({pk_cols})"
    sql = f"CREATE TABLE IF NOT EXISTS {_quote(table_name)} ({column_defs}{pk_clause})"
    execute_query(sql, db_path=db_path)


def upsert_rows(
    table_name: str,
    headers: List[str],
    rows: List[List[Any]],
    primary_keys: List[str],
    date_cols: Optional[List[str]] = None,
    db_path: Optional[str] = None,
) -> int:
    if not rows:
        return 0
    ensure_table(table_name, headers, primary_keys, db_path)

    date_cols = date_cols or []
    placeholders = ", ".join(["?" for _ in headers])
    column_list = ", ".join([_quote(c) for c in headers])

    non_pk_headers = [h for h in headers if h not in primary_keys]
    update_clause = ", ".join([f"{_quote(col)}=excluded.{_quote(col)}" for col in non_pk_headers])

    insert_sql = f"INSERT INTO {_quote(table_name)} ({column_list}) VALUES ({placeholders})"
    if update_clause:
        conflict_cols = ", ".join([_quote(col) for col in primary_keys])
        insert_sql += f" ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_clause}"

    processed_rows = []
    for row in rows:
        item = []
        for idx, value in enumerate(row):
            col = headers[idx]
            parsed = _normalize_date(value) if col in date_cols else value
            item.append(_coerce_value(parsed))
        processed_rows.append(item)

    with transaction(db_path) as conn:
        conn.executemany(insert_sql, processed_rows)
    return len(processed_rows)


def load_csv_and_upsert(
    csv_path: str,
    table_name: str,
    primary_keys: List[str],
    date_cols: Optional[List[str]] = None,
    db_path: Optional[str] = None,
) -> int:
    if not os.path.exists(csv_path):
        return 0
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        if not headers:
            return 0
        rows = [row for row in reader if row]
    return upsert_rows(table_name, headers, rows, primary_keys, date_cols=date_cols, db_path=db_path)


def sync_csv_to_table(csv_filename: str, db_path: Optional[str] = None) -> int:
    save_path = os.getenv("SAVE_PATH", os.getcwd())
    csv_path = os.path.join(save_path, csv_filename)

    for table_name, cfg in TABLE_CONFIG.items():
        if cfg["csv"] == csv_filename:
            return load_csv_and_upsert(csv_path, table_name, cfg["pk"], cfg.get("date_cols"), db_path=db_path)
    raise ValueError(f"CSV no configurado para migración: {csv_filename}")


def table_to_dataframe(table_name: str, db_path: Optional[str] = None):
    import pandas as pd

    rows = fetch_all(f"SELECT * FROM {_quote(table_name)}", db_path=db_path)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([dict(r) for r in rows])
