#!/usr/bin/env python3
"""Migra todos los CSV principales de AI Fitness hacia SQLite sin borrar los CSV."""

import os
from dotenv import load_dotenv

from src.database import TABLE_CONFIG, get_db_path, load_csv_and_upsert


def main() -> None:
    load_dotenv()
    save_path = os.getenv("SAVE_PATH", os.getcwd())
    db_path = get_db_path()

    print(f"Directorio de origen CSV: {save_path}")
    print(f"Base destino SQLite: {db_path}")

    migrated_total = 0
    for table_name, config in TABLE_CONFIG.items():
        csv_path = os.path.join(save_path, config["csv"])
        inserted = load_csv_and_upsert(
            csv_path=csv_path,
            table_name=table_name,
            primary_keys=config["pk"],
            date_cols=config.get("date_cols"),
            db_path=db_path,
        )
        print(f"- {table_name}: {inserted} filas procesadas desde {config['csv']}")
        migrated_total += inserted

    print(f"Migración completada. Filas totales procesadas: {migrated_total}")
    print("Los archivos CSV se mantienen intactos para validación y rollback.")


if __name__ == "__main__":
    main()
