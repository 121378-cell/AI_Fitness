import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class IntegrationPipelineTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]

    def _write_fixtures(self, base_dir: str) -> None:
        Path(base_dir, "garmin_stats.csv").write_text(
            "Date,Steps,RHR,Weight (lbs)\n"
            "2026-01-01,8000,58,170.5\n",
            encoding="utf-8",
        )
        Path(base_dir, "garmin_activities.csv").write_text(
            "activityId,Date,activityName,sportType,distance\n"
            "1,2026-01-01,Morning Run,running,5.2\n",
            encoding="utf-8",
        )
        Path(base_dir, "garmin_runs.csv").write_text(
            "Date,Time,activityName,averageSpeed,averageHR,activityType_typeKey\n"
            "2026-01-01,07:00:00,Morning Run,3.2,145,running\n",
            encoding="utf-8",
        )

    def test_pipeline_script_with_fixtures_outputs_success_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write_fixtures(tmp)
            output_json = Path(tmp, "pipeline_summary.json")

            env = os.environ.copy()
            env["SAVE_PATH"] = tmp
            env["AI_FITNESS_LOG_LEVEL"] = "INFO"

            result = subprocess.run(
                [
                    sys.executable,
                    "run_migration_quality_pipeline.py",
                    "--output-json",
                    str(output_json),
                ],
                cwd=self.repo_root,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, msg=result.stdout + "\n" + result.stderr)
            self.assertTrue(output_json.exists())

            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["passed"])
            self.assertEqual(payload["validations_run"], 3)
            self.assertEqual(payload["total_rows_processed"], 3)
            self.assertFalse(payload["failures"])

    def test_quality_gate_script_returns_success_after_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write_fixtures(tmp)
            env = os.environ.copy()
            env["SAVE_PATH"] = tmp
            env["AI_FITNESS_LOG_LEVEL"] = "INFO"

            migrate = subprocess.run(
                [sys.executable, "migrate_csv_to_sqlite.py"],
                cwd=self.repo_root,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(migrate.returncode, 0, msg=migrate.stdout + "\n" + migrate.stderr)

            qg_json = Path(tmp, "quality_gate_summary.json")
            quality = subprocess.run(
                [
                    sys.executable,
                    "run_data_quality_gate.py",
                    "--output-json",
                    str(qg_json),
                ],
                cwd=self.repo_root,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(quality.returncode, 0, msg=quality.stdout + "\n" + quality.stderr)
            payload = json.loads(qg_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["passed"])
            self.assertEqual(payload["validations_run"], 3)


if __name__ == "__main__":
    unittest.main()
