from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V2_ROOT / "src"))

from henan_v2.config import ConfigError, load_config  # noqa: E402


class ConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config_path = V2_ROOT / "configs" / "train.json"

    def test_default_config_has_canonical_class_order(self) -> None:
        config = load_config(self.config_path)
        self.assertEqual(
            list(config.class_to_idx),
            [
                "luoyang_peony",
                "zhengzhou_bronze_artifact",
                "xinyang_maojian_tea_plant",
            ],
        )
        self.assertEqual(config.class_to_idx["zhengzhou_bronze_artifact"], 1)
        self.assertEqual(config.data.image_size, 192)
        self.assertEqual(config.data.num_workers, 0)
        self.assertEqual(config.training.finetune_epochs, 0)
        self.assertEqual(len(config.fingerprint), 64)

    def test_unknown_key_fails_closed(self) -> None:
        raw = json.loads(self.config_path.read_text(encoding="utf-8"))
        raw["training"]["mystery_option"] = True
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad.json"
            path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ConfigError, "unknown keys"):
                load_config(path)

    def test_duplicate_class_slug_is_rejected(self) -> None:
        raw = json.loads(self.config_path.read_text(encoding="utf-8"))
        raw["data"]["classes"][2]["slug"] = raw["data"]["classes"][0]["slug"]
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad.json"
            path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ConfigError, "duplicate slugs"):
                load_config(path)

    def test_deterministic_resume_rejects_worker_process_rng_gap(self) -> None:
        raw = json.loads(self.config_path.read_text(encoding="utf-8"))
        raw["data"]["num_workers"] = 2
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad.json"
            path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ConfigError, "num_workers must be 0"):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
