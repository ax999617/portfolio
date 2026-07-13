from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


V2_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V2_ROOT / "src"))

from henan_v2.checkpoint import load_checkpoint  # noqa: E402


class TrainingSmokeTests(unittest.TestCase):
    @staticmethod
    def _write_image(path: Path, color: tuple[int, int, int]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (48, 48), color=color).save(path, format="PNG")

    def test_one_epoch_cli_and_resume_without_real_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_root = root / "synthetic_data"
            output_dir = root / "synthetic_run"
            raw_config = json.loads(
                (V2_ROOT / "configs" / "train.json").read_text(encoding="utf-8")
            )
            raw_config["data"]["image_size"] = 96
            raw_config["data"]["resize_size"] = 110
            raw_config["data"]["num_workers"] = 0
            raw_config["model"]["pretrained"] = False
            raw_config["training"]["batch_size"] = 6
            raw_config["training"]["head_epochs"] = 1
            raw_config["training"]["finetune_epochs"] = 1
            config_path = root / "synthetic_config.json"
            config_path.write_text(
                json.dumps(raw_config, ensure_ascii=False), encoding="utf-8"
            )

            class_names = [item["slug"] for item in raw_config["data"]["classes"]]
            for split_index, split in enumerate(("train", "val")):
                count = 2 if split == "train" else 1
                for class_index, class_name in enumerate(class_names):
                    for image_index in range(count):
                        color = (
                            10 + split_index * 90 + image_index,
                            20 + class_index * 60,
                            30 + split_index * 20 + class_index * 3,
                        )
                        self._write_image(
                            data_root
                            / split
                            / class_name
                            / f"sample_{image_index}.png",
                            color,
                        )

            command = [
                sys.executable,
                str(V2_ROOT / "train.py"),
                "--config",
                str(config_path),
                "--data-root",
                str(data_root),
                "--output-dir",
                str(output_dir),
                "--device",
                "cpu",
            ]
            result = subprocess.run(
                command,
                cwd=V2_ROOT,
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in ("best.pt", "last.pt", "history.jsonl", "summary.json"):
                self.assertTrue((output_dir / name).is_file(), name)
            checkpoint = load_checkpoint(output_dir / "best.pt")
            self.assertIn(checkpoint["training_state"]["global_epoch"], (1, 2))
            last_checkpoint = load_checkpoint(output_dir / "last.pt")
            self.assertEqual(last_checkpoint["training_state"]["global_epoch"], 2)
            self.assertEqual(last_checkpoint["training_state"]["stage"], "finetune")

            overwrite_result = subprocess.run(
                command,
                cwd=V2_ROOT,
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
            )
            self.assertNotEqual(overwrite_result.returncode, 0)
            self.assertIn("Refusing to overwrite", overwrite_result.stderr)

            resume_result = subprocess.run(
                command + ["--resume", str(output_dir / "last.pt")],
                cwd=V2_ROOT,
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
            )
            self.assertEqual(resume_result.returncode, 0, resume_result.stderr)


if __name__ == "__main__":
    unittest.main()
