from dataclasses import dataclass
from typing import Dict, Optional

from src.database import TABLE_CONFIG, sync_all_configured_csv, sync_csv_to_table


@dataclass
class SyncResult:
    name: str
    rows_processed: int


def sync_single_dataset(csv_filename: str, db_path: Optional[str] = None) -> SyncResult:
    rows = sync_csv_to_table(csv_filename, db_path=db_path)
    return SyncResult(name=csv_filename, rows_processed=rows)


def sync_all_datasets(db_path: Optional[str] = None) -> Dict[str, SyncResult]:
    raw = sync_all_configured_csv(db_path=db_path)
    results: Dict[str, SyncResult] = {}
    for table_name, rows in raw.items():
        csv_name = TABLE_CONFIG[table_name]["csv"]
        results[table_name] = SyncResult(name=csv_name, rows_processed=rows)
    return results
