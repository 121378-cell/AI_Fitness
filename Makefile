.PHONY: migrate validate quality pipeline ci-check

migrate:
	python migrate_csv_to_sqlite.py

validate:
	python sqlite_validation_examples.py

quality:
	python run_data_quality_gate.py

pipeline:
	AI_FITNESS_LOG_LEVEL=INFO python run_migration_quality_pipeline.py

ci-check:
	python -m py_compile src/database.py src/runtime_checks.py src/http_utils.py src/logging_utils.py src/config/datasets.py src/services/sync_service.py src/services/validation_service.py src/services/quality_gate_service.py src/services/pipeline_service.py migrate_csv_to_sqlite.py sqlite_validation_examples.py run_data_quality_gate.py run_migration_quality_pipeline.py
	AI_FITNESS_LOG_LEVEL=INFO python run_migration_quality_pipeline.py
