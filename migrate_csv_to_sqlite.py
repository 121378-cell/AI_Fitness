#!/usr/bin/env python3
"""Migra todos los CSV principales de AI Fitness hacia SQLite sin borrar los CSV."""

import os
from dotenv import load_dotenv

from src.database import get_db_path
from src.services.sync_service import sync_all_datasets


def main() -> None:
    load_dotenv()
    save_path = os.getenv("SAVE_PATH", os.getcwd())
    db_path = get_db_path()

    print(f"Directorio de origen CSV: {save_path}")
    print(f"Base destino SQLite: {db_path}")

    results = sync_all_datasets(db_path=db_path)
    migrated_total = 0
    for table_name, result in results.items():
        print(f"- {table_name}: {result.rows_processed} filas procesadas desde {result.name}")
        migrated_total += result.rows_processed

    print(f"Migración completada. Filas totales procesadas: {migrated_total}")
    print("Los archivos CSV se mantienen intactos para validación y rollback.")


if __name__ == "__main__":
    main()
