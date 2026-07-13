from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


V2_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V2_ROOT / "src"))

from henan_v2.audit import audit_dataset  # noqa: E402
from henan_v2.config import load_config  # noqa: E402


class DatasetAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config(V2_ROOT / "configs" / "train.json")

    @staticmethod
    def _write_image(path: Path, color: tuple[int, int, int]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (10, 10), color=color).save(path, format="PNG")

    def test_complete_flat_archive_is_source_complete_but_not_training_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for index, item in enumerate(self.config.data.classes):
                self._write_image(
                    root / item.source_directory / "sample.png",
                    (20 + index * 40, 30, 40),
                )
            report = audit_dataset(root, self.config)
            self.assertEqual(report["layout"], "flat_source_archive")
            self.assertTrue(report["source_complete"])
            self.assertFalse(report["training_ready"])
            self.assertEqual(report["issues"], [])
            self.assertNotIn("sample_count", report)

    def test_incomplete_flat_archive_reports_missing_class(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for index, item in enumerate(self.config.data.classes[:-1]):
                self._write_image(
                    root / item.source_directory / "sample.png",
                    (20 + index * 40, 30, 40),
                )
            report = audit_dataset(root, self.config)
            self.assertFalse(report["source_complete"])
            self.assertEqual(
                report["missing_source_directories"],
                [self.config.data.classes[-1].source_directory],
            )
            self.assertEqual(report["issues"][0]["code"], "missing_source_class")

    def test_prepared_split_contract_can_be_training_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for split_index, split in enumerate(("train", "val")):
                for class_index, slug in enumerate(self.config.class_to_idx):
                    self._write_image(
                        root / split / slug / "sample.png",
                        (20 + split_index * 80, 30 + class_index * 50, 40),
                    )
            report = audit_dataset(root, self.config)
            self.assertEqual(report["layout"], "prepared_splits")
            self.assertTrue(report["source_complete"])
            self.assertTrue(report["training_ready"])

    def test_flat_archive_with_unreadable_image_is_not_source_complete(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for index, item in enumerate(self.config.data.classes):
                self._write_image(
                    root / item.source_directory / "sample.png",
                    (20 + index * 40, 30, 40),
                )
            broken = root / self.config.data.classes[0].source_directory / "broken.jpg"
            broken.write_bytes(b"not an image")
            report = audit_dataset(root, self.config)
            self.assertFalse(report["source_complete"])
            self.assertFalse(report["training_ready"])
            self.assertEqual(report["issues"][0]["code"], "unreadable_image")
            self.assertIn("broken.jpg", report["unreadable_images"][0])

    def test_prepared_split_with_unreadable_image_is_not_training_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for split_index, split in enumerate(("train", "val")):
                for class_index, slug in enumerate(self.config.class_to_idx):
                    self._write_image(
                        root / split / slug / "sample.png",
                        (20 + split_index * 80, 30 + class_index * 50, 40),
                    )
            broken = root / "train" / next(iter(self.config.class_to_idx)) / "broken.jpg"
            broken.write_bytes(b"not an image")
            report = audit_dataset(root, self.config)
            self.assertFalse(report["training_ready"])
            self.assertEqual(report["issues"][0]["code"], "unreadable_image")
            self.assertIn("broken.jpg", report["issues"][0]["message"])


if __name__ == "__main__":
    unittest.main()
