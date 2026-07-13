from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from check_plan_test_v1 import EXPECTED_CSV, FROZEN_ASSETS, build_read_only_plan  # noqa: E402


class ReadOnlyPlanTests(unittest.TestCase):
    def test_required_file_presence_is_reported_without_output_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for relative in EXPECTED_CSV + FROZEN_ASSETS:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
            before = sorted(str(path.relative_to(root)) for path in root.rglob("*"))
            plan = build_read_only_plan(root)
            after = sorted(str(path.relative_to(root)) for path in root.rglob("*"))
            self.assertTrue(plan["required_files_present"])
            self.assertFalse(plan["safe_to_run_legacy"])
            self.assertEqual(before, after)

    def test_missing_sources_fail_presence_check_without_repair(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan = build_read_only_plan(root)
            self.assertFalse(plan["required_files_present"])
            self.assertFalse(any(item["exists"] for item in plan["source_csv"]))
            self.assertEqual(list(root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
