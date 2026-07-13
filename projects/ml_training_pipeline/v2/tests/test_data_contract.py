from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


V2_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V2_ROOT / "src"))

from henan_v2.config import load_config  # noqa: E402
from henan_v2.data import DataContractError, build_datasets  # noqa: E402


class DataContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config(V2_ROOT / "configs" / "train.json")
        self.class_names = list(self.config.class_to_idx)

    @staticmethod
    def _write_image(path: Path, color: tuple[int, int, int]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (12, 12), color=color).save(path, format="PNG")

    def _make_complete_splits(self, root: Path) -> None:
        for split_index, split in enumerate(("train", "val", "test")):
            for class_index, class_name in enumerate(self.class_names):
                color = (
                    20 + split_index * 50,
                    30 + class_index * 60,
                    40 + split_index * 20 + class_index,
                )
                self._write_image(root / split / class_name / "sample.png", color)

    def test_config_order_overrides_imagefolder_sorting(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._make_complete_splits(root)
            bundle = build_datasets(root, self.config)
            self.assertEqual(bundle.train.classes, self.class_names)
            self.assertEqual(bundle.train.class_to_idx, self.config.class_to_idx)
            self.assertEqual(bundle.train.class_to_idx["zhengzhou_bronze_artifact"], 1)

    def test_missing_class_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._make_complete_splits(root)
            shutil.rmtree(root / "val" / self.class_names[-1])
            with self.assertRaisesRegex(DataContractError, "missing"):
                build_datasets(root, self.config)

    def test_byte_identical_cross_split_image_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._make_complete_splits(root)
            source = root / "train" / self.class_names[0] / "sample.png"
            destination = root / "val" / self.class_names[1] / "copied.png"
            destination.write_bytes(source.read_bytes())
            with self.assertRaisesRegex(DataContractError, "Byte-identical"):
                build_datasets(root, self.config)


if __name__ == "__main__":
    unittest.main()
