from __future__ import annotations

import random
import time
from contextlib import nullcontext
from typing import Any

import torch
from torch import nn
from torch.utils.data import DataLoader

from .metrics import ClassificationMeter
from .models import set_frozen_batchnorm_eval


class TrainingError(RuntimeError):
    """Raised when the requested runtime cannot execute training safely."""


def resolve_device(requested: str) -> torch.device:
    if requested == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        mps = getattr(torch.backends, "mps", None)
        if mps is not None and mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    if requested == "cuda" and not torch.cuda.is_available():
        raise TrainingError("CUDA was requested but is not available")
    if requested == "mps":
        mps = getattr(torch.backends, "mps", None)
        if mps is None or not mps.is_available():
            raise TrainingError("MPS was requested but is not available")
    if requested not in {"cpu", "cuda", "mps"}:
        raise TrainingError(f"Unsupported device: {requested}")
    return torch.device(requested)


def seed_everything(seed: int, deterministic: bool) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if deterministic:
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True
        torch.use_deterministic_algorithms(True, warn_only=True)


def create_grad_scaler(device: torch.device, requested_amp: bool) -> tuple[Any, bool]:
    enabled = requested_amp and device.type == "cuda"
    scaler_device = "cuda" if enabled else "cpu"
    return torch.amp.GradScaler(scaler_device, enabled=enabled), enabled


def run_epoch(
    *,
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    num_classes: int,
    optimizer: torch.optim.Optimizer | None = None,
    scaler: Any | None = None,
    amp_enabled: bool = False,
) -> dict[str, object]:
    training = optimizer is not None
    if training and scaler is None:
        raise TrainingError("A GradScaler is required for a training epoch")

    model.train(training)
    if training:
        set_frozen_batchnorm_eval(model)
    meter = ClassificationMeter(num_classes=num_classes)
    started = time.perf_counter()

    for images, targets in loader:
        images = images.to(device, non_blocking=device.type == "cuda")
        targets = targets.to(device, non_blocking=device.type == "cuda")
        if training:
            optimizer.zero_grad(set_to_none=True)

        grad_context = torch.enable_grad() if training else torch.inference_mode()
        amp_context = (
            torch.amp.autocast("cuda", dtype=torch.float16)
            if amp_enabled
            else nullcontext()
        )
        with grad_context:
            with amp_context:
                logits = model(images)
                loss = criterion(logits, targets)
            if training:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()

        meter.update(logits, targets, float(loss.detach().item()))

    result = meter.compute()
    result["seconds"] = time.perf_counter() - started
    return result
