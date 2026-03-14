#!/usr/bin/env python3
"""Minimal coverage gate using stdlib trace (no external deps)."""

import argparse
import os
import runpy
import sys
import trace
from pathlib import Path


def collect_source_files(src_root: Path):
    return [p for p in src_root.rglob("*.py") if p.is_file()]


def executable_lines(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    total = 0
    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        total += 1
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description="Run unittest suite and enforce src coverage threshold")
    parser.add_argument("--fail-under", type=float, default=70.0)
    args = parser.parse_args()

    repo = Path(__file__).resolve().parent
    src_root = repo / "src"
    if not src_root.exists():
        print("src directory not found")
        return 1

    tracer = trace.Trace(count=1, trace=0)

    def _run_tests():
        import unittest

        suite = unittest.defaultTestLoader.loadTestsFromNames(
            [
                "tests.test_services",
                "tests.test_config_settings",
                "tests.test_database_migrations",
                "tests.test_integration_pipeline",
            ]
        )
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)

    try:
        tracer.runfunc(_run_tests)
    except SystemExit as exc:
        return int(exc.code or 1)

    results = tracer.results()
    counts = results.counts

    total_executable = 0
    total_covered = 0

    for f in collect_source_files(src_root):
        rel = str(f.resolve())
        exec_lines = executable_lines(f)
        covered = sum(1 for (filename, _lineno), _v in counts.items() if filename == rel)
        covered = min(covered, exec_lines)
        total_executable += exec_lines
        total_covered += covered

    coverage_pct = 100.0 * total_covered / total_executable if total_executable else 100.0
    print(f"src coverage: {coverage_pct:.2f}% ({total_covered}/{total_executable})")

    if coverage_pct < args.fail_under:
        print(f"Coverage check failed: {coverage_pct:.2f}% < {args.fail_under:.2f}%")
        return 1

    print("Coverage check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
