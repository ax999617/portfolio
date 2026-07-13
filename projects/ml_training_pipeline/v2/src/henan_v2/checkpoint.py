from __future__ import annotations

import math
import os
import random
from pathlib import Path
from typing import Any, Mapping

import torch
import torchvision
from torch import nn

from . import __version__
from .config import ProjectConfig
from .models import SUPPORTED_ARCHITECTURE, build_model


CHECKPOINT_SCHEMA_VERSION = 1


class CheckpointError(RuntimeError):
    """Raised when a checkpoint is corrupt or violates the v2 contract."""


def capture_runtime_state(train_generator: torch.Generator) -> dict[str, Any]:
    return {
        "python_random": random.getstate(),
        "torch_random": torch.get_rng_state(),
        "cuda_random": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [],
        "train_generator": train_generator.get_state(),
    }


def restore_runtime_state(
    checkpoint: Mapping[str, Any], train_generator: torch.Generator
) -> None:
    state = checkpoint.get("runtime_state")
    if not isinstance(state, Mapping):
        raise CheckpointError("Checkpoint is missing runtime_state")
    try:
        random.setstate(state["python_random"])
        torch.set_rng_state(state["torch_random"])
        train_generator.set_state(state["train_generator"])
        cuda_state = state.get("cuda_random", [])
        if torch.cuda.is_available() and cuda_state:
            torch.cuda.set_rng_state_all(cuda_state)
    except (KeyError, TypeError, RuntimeError) as exc:
        raise CheckpointError(f"Cannot restore runtime state: {exc}") from exc


def build_checkpoint_payload(
    *,
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: Any,
    scaler: torch.amp.GradScaler,
    config: ProjectConfig,
    stage: str,
    stage_index: int,
    stage_epoch: int,
    global_epoch: int,
    best_val_loss: float,
    best_epoch: int,
    bad_epochs: int,
    metrics: Mapping[str, Any],
    train_generator: torch.Generator,
) -> dict[str, Any]:
    return {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "pipeline_version": __version__,
        "config_fingerprint": config.fingerprint,
        "model_contract": {
            "architecture": config.model.architecture,
            "num_classes": len(config.data.classes),
            "dropout": config.model.dropout,
            "pretrained_weights": config.model.pretrained_weights,
        },
        "class_to_idx": config.class_to_idx,
        "display_names": config.display_names,
        "preprocessing": config.preprocessing_contract,
        "training_state": {
            "stage": stage,
            "stage_index": stage_index,
            "stage_epoch": stage_epoch,
            "global_epoch": global_epoch,
            "best_val_loss": float(best_val_loss),
            "best_epoch": best_epoch,
            "bad_epochs": bad_epochs,
            "seed": config.training.seed,
        },
        "metrics": dict(metrics),
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "scheduler_state_dict": scheduler.state_dict(),
        "scaler_state_dict": scaler.state_dict(),
        "runtime_state": capture_runtime_state(train_generator),
        "versions": {
            "python_compatible": "3.10+",
            "torch": str(torch.__version__),
            "torchvision": str(torchvision.__version__),
        },
    }


def save_checkpoint_atomic(payload: Mapping[str, Any], path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    try:
        torch.save(dict(payload), temporary)
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_checkpoint(path: str | Path) -> dict[str, Any]:
    checkpoint_path = Path(path)
    if not checkpoint_path.is_file():
        raise CheckpointError(f"Checkpoint does not exist: {checkpoint_path}")
    try:
        payload = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    except Exception as exc:
        raise CheckpointError(f"Cannot safely load checkpoint {checkpoint_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckpointError("Checkpoint root must be a dictionary")
    _validate_structure(payload)
    return payload


def _validate_structure(checkpoint: Mapping[str, Any]) -> None:
    required = {
        "schema_version",
        "pipeline_version",
        "config_fingerprint",
        "model_contract",
        "class_to_idx",
        "display_names",
        "preprocessing",
        "training_state",
        "model_state_dict",
    }
    missing = required - set(checkpoint)
    if missing:
        raise CheckpointError(f"Checkpoint is missing keys: {sorted(missing)}")
    if checkpoint["schema_version"] != CHECKPOINT_SCHEMA_VERSION:
        raise CheckpointError(
            f"Unsupported checkpoint schema_version: {checkpoint['schema_version']}"
        )
    if not isinstance(checkpoint["model_state_dict"], Mapping):
        raise CheckpointError("model_state_dict must be a dictionary")
    class_to_idx = checkpoint["class_to_idx"]
    if not isinstance(class_to_idx, Mapping) or not class_to_idx:
        raise CheckpointError("class_to_idx must be a non-empty dictionary")
    if not all(
        isinstance(name, str) and name and type(index) is int
        for name, index in class_to_idx.items()
    ):
        raise CheckpointError("class_to_idx must map non-empty strings to integers")
    expected_indices = list(range(len(class_to_idx)))
    if sorted(class_to_idx.values()) != expected_indices:
        raise CheckpointError("class_to_idx indices must be contiguous from zero")
    display_names = checkpoint["display_names"]
    if not isinstance(display_names, Mapping) or set(display_names) != set(class_to_idx):
        raise CheckpointError("display_names must have the same keys as class_to_idx")
    if not all(isinstance(value, str) and value for value in display_names.values()):
        raise CheckpointError("display_names values must be non-empty strings")
    model_contract = checkpoint["model_contract"]
    if not isinstance(model_contract, Mapping):
        raise CheckpointError("model_contract must be a dictionary")
    preprocessing = checkpoint["preprocessing"]
    if not isinstance(preprocessing, Mapping):
        raise CheckpointError("preprocessing must be a dictionary")
    try:
        image_size = preprocessing["image_size"]
        resize_size = preprocessing["resize_size"]
        mean = preprocessing["normalization_mean"]
        std = preprocessing["normalization_std"]
        valid_sizes = (
            type(image_size) is int
            and type(resize_size) is int
            and image_size >= 96
            and resize_size >= image_size
        )
        valid_mean = (
            isinstance(mean, (list, tuple))
            and len(mean) == 3
            and all(isinstance(item, (int, float)) and math.isfinite(float(item)) for item in mean)
        )
        valid_std = (
            isinstance(std, (list, tuple))
            and len(std) == 3
            and all(
                isinstance(item, (int, float))
                and math.isfinite(float(item))
                and float(item) > 0
                for item in std
            )
        )
    except (KeyError, TypeError, ValueError):
        valid_sizes = valid_mean = valid_std = False
    if not valid_sizes or not valid_mean or not valid_std:
        raise CheckpointError("preprocessing contract is invalid")
    if not isinstance(checkpoint["training_state"], Mapping):
        raise CheckpointError("training_state must be a dictionary")


def validate_checkpoint_against_config(
    checkpoint: Mapping[str, Any], config: ProjectConfig
) -> None:
    mismatches: list[str] = []
    if checkpoint.get("config_fingerprint") != config.fingerprint:
        mismatches.append("config_fingerprint")
    if dict(checkpoint.get("class_to_idx", {})) != config.class_to_idx:
        mismatches.append("class_to_idx")
    if dict(checkpoint.get("display_names", {})) != config.display_names:
        mismatches.append("display_names")
    if dict(checkpoint.get("preprocessing", {})) != config.preprocessing_contract:
        mismatches.append("preprocessing")
    contract = checkpoint.get("model_contract", {})
    expected_contract = {
        "architecture": config.model.architecture,
        "num_classes": len(config.data.classes),
        "dropout": config.model.dropout,
        "pretrained_weights": config.model.pretrained_weights,
    }
    if dict(contract) != expected_contract:
        mismatches.append("model_contract")
    if mismatches:
        raise CheckpointError(
            "Checkpoint does not match the active configuration: " + ", ".join(mismatches)
        )


def load_best_checkpoint(
    path: str | Path,
    config: ProjectConfig,
    *,
    expected_best_epoch: int | None = None,
    expected_best_val_loss: float | None = None,
) -> dict[str, Any]:
    """Load a best checkpoint and verify both its semantics and run metadata."""

    checkpoint = load_checkpoint(path)
    validate_checkpoint_against_config(checkpoint, config)
    state = checkpoint["training_state"]
    try:
        global_epoch = state["global_epoch"]
        best_epoch = state["best_epoch"]
        best_val_loss = float(state["best_val_loss"])
    except (KeyError, TypeError, ValueError) as exc:
        raise CheckpointError(f"Best checkpoint has invalid training_state: {exc}") from exc
    if type(global_epoch) is not int or global_epoch < 1:
        raise CheckpointError("Best checkpoint global_epoch must be a positive integer")
    if type(best_epoch) is not int or best_epoch < 1:
        raise CheckpointError("Best checkpoint best_epoch must be a positive integer")
    if global_epoch != best_epoch:
        raise CheckpointError(
            "Best checkpoint must contain the model from its own best_epoch"
        )
    if not math.isfinite(best_val_loss):
        raise CheckpointError("Best checkpoint best_val_loss must be finite")
    if expected_best_epoch is not None and best_epoch != expected_best_epoch:
        raise CheckpointError(
            "Best and last checkpoint metadata disagree: "
            f"best_epoch={best_epoch}, expected={expected_best_epoch}"
        )
    if (
        expected_best_val_loss is not None
        and best_val_loss != expected_best_val_loss
    ):
        raise CheckpointError(
            "Best and last checkpoint metadata disagree: "
            f"best_val_loss={best_val_loss}, expected={expected_best_val_loss}"
        )
    return checkpoint


def restore_model(checkpoint: Mapping[str, Any], device: torch.device) -> nn.Module:
    _validate_structure(checkpoint)
    contract = checkpoint["model_contract"]
    if not isinstance(contract, Mapping):
        raise CheckpointError("model_contract must be a dictionary")
    try:
        architecture = str(contract["architecture"])
        num_classes = int(contract["num_classes"])
        dropout = float(contract["dropout"])
        pretrained_weights = str(contract["pretrained_weights"])
    except (KeyError, TypeError, ValueError) as exc:
        raise CheckpointError(f"Invalid model_contract: {exc}") from exc
    if architecture != SUPPORTED_ARCHITECTURE:
        raise CheckpointError(f"Unsupported checkpoint architecture: {architecture}")
    if pretrained_weights != "MobileNet_V3_Small_Weights.IMAGENET1K_V1":
        raise CheckpointError(
            f"Unsupported checkpoint pretrained_weights: {pretrained_weights}"
        )
    if num_classes != len(checkpoint["class_to_idx"]):
        raise CheckpointError("model_contract num_classes disagrees with class_to_idx")

    try:
        model = build_model(
            num_classes=num_classes,
            pretrained=False,
            dropout=dropout,
            architecture=architecture,
        )
    except ValueError as exc:
        raise CheckpointError(f"Invalid model contract: {exc}") from exc
    try:
        model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    except (RuntimeError, TypeError) as exc:
        raise CheckpointError(f"Model parameters fail strict loading: {exc}") from exc
    return model.to(device)
