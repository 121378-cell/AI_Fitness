from dataclasses import dataclass
from typing import Dict, Optional

from src.database import TABLE_CONFIG, sync_all_configured_csv, sync_csv_to_table
from src.logging_utils import get_logger

logger = get_logger("ai_fitness.sync_service")


@dataclass
class SyncResult:
    name: str
    rows_processed: int


def sync_single_dataset(csv_filename: str, db_path: Optional[str] = None) -> SyncResult:
    logger.info("Starting SQLite sync for dataset: %s", csv_filename)
    rows = sync_csv_to_table(csv_filename, db_path=db_path)
    logger.info("Completed SQLite sync for dataset: %s (rows=%s)", csv_filename, rows)
    return SyncResult(name=csv_filename, rows_processed=rows)


def sync_all_datasets(db_path: Optional[str] = None) -> Dict[str, SyncResult]:
    logger.info("Starting SQLite full sync for all configured datasets")
    raw = sync_all_configured_csv(db_path=db_path)
    results: Dict[str, SyncResult] = {}
    for table_name, rows in raw.items():
        csv_name = TABLE_CONFIG[table_name]["csv"]
        logger.info("Table %s synced from %s (rows=%s)", table_name, csv_name, rows)
        results[table_name] = SyncResult(name=csv_name, rows_processed=rows)
    logger.info("Completed SQLite full sync")
    return results
