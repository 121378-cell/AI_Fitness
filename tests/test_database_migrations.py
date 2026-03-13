import os
import sqlite3
import tempfile
import unittest

from src.database import SCHEMA_VERSION, apply_schema_migrations


class DatabaseMigrationsTests(unittest.TestCase):
    def test_apply_schema_migrations_sets_user_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "ai_fitness.db")
            version = apply_schema_migrations(db_path=db_path)
            self.assertEqual(version, SCHEMA_VERSION)
            with sqlite3.connect(db_path) as conn:
                current = conn.execute("PRAGMA user_version").fetchone()[0]
            self.assertEqual(current, SCHEMA_VERSION)

    def test_migration_v1_adds_ingested_at_when_table_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "ai_fitness.db")
            with sqlite3.connect(db_path) as conn:
                conn.execute('CREATE TABLE garmin_stats ("Date" TEXT PRIMARY KEY, "Steps" INTEGER)')
                conn.execute("PRAGMA user_version = 0")

            apply_schema_migrations(db_path=db_path)

            with sqlite3.connect(db_path) as conn:
                cols = [row[1] for row in conn.execute("PRAGMA table_info('garmin_stats')").fetchall()]
                user_version = conn.execute("PRAGMA user_version").fetchone()[0]
            self.assertIn("ingested_at", cols)
            self.assertEqual(user_version, SCHEMA_VERSION)


if __name__ == "__main__":
    unittest.main()
