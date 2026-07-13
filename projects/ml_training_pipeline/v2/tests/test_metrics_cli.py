from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import torch


V2_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V2_ROOT / "src"))

from henan_v2.metrics import ClassificationMeter  # noqa: E402


class MetricsAndCliTests(unittest.TestCase):
    def test_metrics_fixture(self) -> None:
        targets = torch.tensor([0, 0, 1, 1, 2, 2])
        predictions = torch.tensor([0, 1, 1, 1, 0, 0])
        logits = torch.full((6, 3), -5.0)
        logits[torch.arange(6), predictions] = 5.0
        meter = ClassificationMeter(num_classes=3)
        meter.update(logits, targets, loss=0.25)
        result = meter.compute()
        self.assertEqual(result["confusion_matrix"], [[1, 1, 0], [0, 2, 0], [2, 0, 0]])
        self.assertAlmostEqual(float(result["accuracy"]), 0.5)
        self.assertAlmostEqual(float(result["macro_f1"]), 0.4)
        self.assertAlmostEqual(float(result["loss"]), 0.25)

    def test_empty_metrics_fail(self) -> None:
        with self.assertRaisesRegex(ValueError, "empty"):
            ClassificationMeter(num_classes=3).compute()

    def test_cli_help_does_not_create_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "runs"
            result = subprocess.run(
                [sys.executable, str(V2_ROOT / "train.py"), "--help"],
                cwd=V2_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(output.exists())

    def test_missing_dataset_fails_before_output_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output = root / "runs"
            result = subprocess.run(
                [
                    sys.executable,
                    str(V2_ROOT / "train.py"),
                    "--data-root",
                    str(root / "missing"),
                    "--output-dir",
                    str(output),
                    "--device",
                    "cpu",
                ],
                cwd=V2_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
