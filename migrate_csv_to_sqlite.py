#!/usr/bin/env python3
"""Migra todos los CSV principales de AI Fitness hacia SQLite sin borrar los CSV."""

import os
from dotenv import load_dotenv

from src.database import get_db_path
from src.logging_utils import get_logger
from src.services.sync_service import sync_all_datasets

logger = get_logger("ai_fitness.migrate")


def main() -> None:
    load_dotenv()
    save_path = os.getenv("SAVE_PATH", os.getcwd())
    db_path = get_db_path()

    logger.info("Directorio de origen CSV: %s", save_path)
    logger.info("Base destino SQLite: %s", db_path)

    results = sync_all_datasets(db_path=db_path)
    migrated_total = 0
    for table_name, result in results.items():
        logger.info("%s: %s filas procesadas desde %s", table_name, result.rows_processed, result.name)
        migrated_total += result.rows_processed

    logger.info("Migración completada. Filas totales procesadas: %s", migrated_total)
    logger.info("Los archivos CSV se mantienen intactos para validación y rollback.")


if __name__ == "__main__":
    main()
