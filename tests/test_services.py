import os
import tempfile
import unittest

from src.config.datasets import get_validation_tables
from src.services.pipeline_service import PipelineSummary
from src.services.quality_gate_service import QualityGateSummary, run_quality_gate
from src.services.sync_service import SyncResult


class ServicesTests(unittest.TestCase):
    def test_get_validation_tables_contains_expected_keys(self):
        tables = get_validation_tables('/tmp/example')
        self.assertIn('garmin_stats', tables)
        self.assertIn('garmin_activities', tables)
        self.assertIn('garmin_runs', tables)

    def test_quality_gate_empty_environment_is_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            tables = get_validation_tables(tmp)
            db_path = os.path.join(tmp, 'ai_fitness.db')
            summary = run_quality_gate(tables, save_path=tmp, db_path=db_path)
            self.assertTrue(summary.passed)
            self.assertEqual(summary.validations_run, 0)
            self.assertEqual(summary.failures, [])

    def test_quality_gate_fails_when_db_missing_but_csv_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            tables = get_validation_tables(tmp)
            csv_path = tables['garmin_stats']['csv']
            with open(csv_path, 'w', encoding='utf-8') as fh:
                fh.write('Date,Steps\n2026-01-01,1000\n')
            db_path = os.path.join(tmp, 'ai_fitness.db')
            summary = run_quality_gate(tables, save_path=tmp, db_path=db_path)
            self.assertFalse(summary.passed)
            self.assertTrue(any('Base SQLite no encontrada' in f for f in summary.failures))

    def test_pipeline_summary_computed_properties(self):
        summary = PipelineSummary(
            sync_results={
                'a': SyncResult(name='a.csv', rows_processed=2),
                'b': SyncResult(name='b.csv', rows_processed=3),
            },
            quality_gate=QualityGateSummary(passed=True, validations_run=2, failures=[]),
        )
        self.assertEqual(summary.total_rows_processed, 5)
        self.assertTrue(summary.passed)


if __name__ == '__main__':
    unittest.main()
