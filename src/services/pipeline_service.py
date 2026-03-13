from dataclasses import dataclass
from typing import Dict, List, Optional

from src.database import get_db_path
from src.logging_utils import get_logger
from src.services.quality_gate_service import QualityGateSummary, run_quality_gate
from src.services.sync_service import SyncResult, sync_all_datasets

logger = get_logger("ai_fitness.pipeline_service")


@dataclass
class PipelineSummary:
    sync_results: Dict[str, SyncResult]
    quality_gate: QualityGateSummary

    @property
    def total_rows_processed(self) -> int:
        return sum(result.rows_processed for result in self.sync_results.values())

    @property
    def passed(self) -> bool:
        return self.quality_gate.passed


def run_migration_and_quality_gate(
    tables: Dict[str, Dict[str, object]],
    save_path: str,
    db_path: Optional[str] = None,
) -> PipelineSummary:
    resolved_db_path = db_path or get_db_path()
    logger.info("Starting migration+quality pipeline (db=%s)", resolved_db_path)

    sync_results = sync_all_datasets(db_path=resolved_db_path)
    quality_gate = run_quality_gate(tables=tables, save_path=save_path, db_path=resolved_db_path)

    logger.info(
        "Pipeline finished (passed=%s, total_rows=%s, validations_run=%s)",
        quality_gate.passed,
        sum(v.rows_processed for v in sync_results.values()),
        quality_gate.validations_run,
    )
    return PipelineSummary(sync_results=sync_results, quality_gate=quality_gate)
