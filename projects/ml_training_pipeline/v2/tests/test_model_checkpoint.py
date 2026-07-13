from __future__ import annotations

import copy
import math
import sys
import tempfile
import unittest
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


V2_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V2_ROOT / "src"))

from henan_v2.checkpoint import (  # noqa: E402
    CheckpointError,
    build_checkpoint_payload,
    load_best_checkpoint,
    load_checkpoint,
    restore_model,
    save_checkpoint_atomic,
    validate_checkpoint_against_config,
)
from henan_v2.config import load_config  # noqa: E402
from henan_v2.engine import create_grad_scaler, run_epoch  # noqa: E402
from henan_v2.models import (  # noqa: E402
    build_model,
    configure_trainable_stage,
)


class ModelAndCheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config(V2_ROOT / "configs" / "train.json")

    def _model(self) -> nn.Module:
        return build_model(
            num_classes=3,
            pretrained=False,
            dropout=self.config.model.dropout,
        )

    def test_cpu_head_only_step_freezes_backbone_and_batchnorm(self) -> None:
        torch.manual_seed(7)
        model = self._model()
        counts = configure_trainable_stage(model, "head", unfreeze_last_blocks=2)
        self.assertLess(counts.trainable, counts.total)
        first_feature_parameter = next(model.features.parameters())  # type: ignore[attr-defined]
        first_batchnorm = next(
            module
            for module in model.features.modules()  # type: ignore[attr-defined]
            if isinstance(module, nn.BatchNorm2d)
        )
        running_mean_before = first_batchnorm.running_mean.clone()
        head_before = model.classifier[-1].weight.detach().clone()  # type: ignore[attr-defined]
        loader = DataLoader(
            TensorDataset(torch.randn(2, 3, 96, 96), torch.tensor([0, 2])),
            batch_size=2,
        )
        optimizer = torch.optim.AdamW(
            [parameter for parameter in model.parameters() if parameter.requires_grad],
            lr=1e-3,
        )
        scaler, amp_enabled = create_grad_scaler(torch.device("cpu"), requested_amp=True)
        self.assertFalse(amp_enabled)
        metrics = run_epoch(
            model=model,
            loader=loader,
            criterion=nn.CrossEntropyLoss(),
            device=torch.device("cpu"),
            num_classes=3,
            optimizer=optimizer,
            scaler=scaler,
            amp_enabled=amp_enabled,
        )
        self.assertTrue(math.isfinite(float(metrics["loss"])))
        self.assertIsNone(first_feature_parameter.grad)
        torch.testing.assert_close(first_batchnorm.running_mean, running_mean_before)
        self.assertFalse(
            torch.equal(model.classifier[-1].weight.detach(), head_before)  # type: ignore[attr-defined]
        )

    def test_finetune_stage_only_unfreezes_feature_suffix_and_head(self) -> None:
        model = self._model()
        configure_trainable_stage(model, "finetune", unfreeze_last_blocks=2)
        self.assertFalse(next(model.features[0].parameters()).requires_grad)  # type: ignore[attr-defined]
        self.assertTrue(next(model.features[-1].parameters()).requires_grad)  # type: ignore[attr-defined]
        self.assertTrue(next(model.classifier.parameters()).requires_grad)  # type: ignore[attr-defined]

    def _checkpoint_payload(self, model: nn.Module) -> dict[str, object]:
        configure_trainable_stage(model, "head", unfreeze_last_blocks=2)
        optimizer = torch.optim.AdamW(
            [parameter for parameter in model.parameters() if parameter.requires_grad],
            lr=1e-3,
        )
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer)
        scaler, _ = create_grad_scaler(torch.device("cpu"), requested_amp=False)
        return build_checkpoint_payload(
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            scaler=scaler,
            config=self.config,
            stage="head",
            stage_index=0,
            stage_epoch=1,
            global_epoch=1,
            best_val_loss=0.5,
            best_epoch=1,
            bad_epochs=0,
            metrics={"val": {"loss": 0.5}},
            train_generator=torch.Generator().manual_seed(42),
        )

    def test_strict_roundtrip_supports_unicode_path(self) -> None:
        torch.manual_seed(11)
        model = self._model().eval()
        payload = self._checkpoint_payload(model)
        sample = torch.randn(1, 3, 96, 96)
        with torch.inference_mode():
            expected = model(sample)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "中文 空格" / "model.pt"
            save_checkpoint_atomic(payload, path)
            checkpoint = load_checkpoint(path)
            validate_checkpoint_against_config(checkpoint, self.config)
            restored = restore_model(checkpoint, torch.device("cpu")).eval()
            with torch.inference_mode():
                actual = restored(sample)
            torch.testing.assert_close(actual, expected)

    def test_missing_weight_and_semantic_mismatch_fail_closed(self) -> None:
        payload = self._checkpoint_payload(self._model())
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            damaged = copy.deepcopy(payload)
            first_key = next(iter(damaged["model_state_dict"]))  # type: ignore[arg-type]
            del damaged["model_state_dict"][first_key]  # type: ignore[index]
            damaged_path = root / "damaged.pt"
            save_checkpoint_atomic(damaged, damaged_path)
            with self.assertRaisesRegex(CheckpointError, "strict loading"):
                restore_model(load_checkpoint(damaged_path), torch.device("cpu"))

            mismatched = copy.deepcopy(payload)
            mismatched["class_to_idx"] = {
                "luoyang_peony": 0,
                "xinyang_maojian_tea_plant": 1,
                "zhengzhou_bronze_artifact": 2,
            }
            mismatch_path = root / "mismatch.pt"
            save_checkpoint_atomic(mismatched, mismatch_path)
            with self.assertRaisesRegex(CheckpointError, "active configuration"):
                validate_checkpoint_against_config(
                    load_checkpoint(mismatch_path), self.config
                )

            invalid_preprocessing = copy.deepcopy(payload)
            invalid_preprocessing["preprocessing"]["normalization_std"] = [0.0, 1.0, 1.0]  # type: ignore[index]
            invalid_path = root / "invalid_preprocessing.pt"
            save_checkpoint_atomic(invalid_preprocessing, invalid_path)
            with self.assertRaisesRegex(CheckpointError, "preprocessing"):
                load_checkpoint(invalid_path)

            corrupt_path = root / "corrupt.pt"
            corrupt_path.write_bytes(b"not a checkpoint")
            with self.assertRaisesRegex(CheckpointError, "safely load"):
                load_checkpoint(corrupt_path)

    def test_best_checkpoint_must_match_its_epoch_and_last_metadata(self) -> None:
        payload = self._checkpoint_payload(self._model())
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            valid_path = root / "valid_best.pt"
            save_checkpoint_atomic(payload, valid_path)
            loaded = load_best_checkpoint(
                valid_path,
                self.config,
                expected_best_epoch=1,
                expected_best_val_loss=0.5,
            )
            self.assertEqual(loaded["training_state"]["global_epoch"], 1)
            with self.assertRaisesRegex(CheckpointError, "metadata disagree"):
                load_best_checkpoint(
                    valid_path,
                    self.config,
                    expected_best_epoch=2,
                    expected_best_val_loss=0.5,
                )

            stale = copy.deepcopy(payload)
            stale["training_state"]["global_epoch"] = 2  # type: ignore[index]
            stale_path = root / "stale_best.pt"
            save_checkpoint_atomic(stale, stale_path)
            with self.assertRaisesRegex(CheckpointError, "own best_epoch"):
                load_best_checkpoint(stale_path, self.config)


if __name__ == "__main__":
    unittest.main()
