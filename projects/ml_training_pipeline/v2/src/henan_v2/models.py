from __future__ import annotations

from dataclasses import dataclass

import torch.nn as nn
from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small
from torchvision.models.mobilenetv3 import MobileNetV3


SUPPORTED_ARCHITECTURE = "mobilenet_v3_small"
SUPPORTED_WEIGHTS = "MobileNet_V3_Small_Weights.IMAGENET1K_V1"


class ModelContractError(ValueError):
    """Raised when model metadata does not match the supported architecture."""


@dataclass(frozen=True)
class ParameterCounts:
    total: int
    trainable: int


def build_model(
    *,
    num_classes: int,
    pretrained: bool,
    dropout: float,
    architecture: str = SUPPORTED_ARCHITECTURE,
) -> MobileNetV3:
    if architecture != SUPPORTED_ARCHITECTURE:
        raise ModelContractError(f"Unsupported architecture: {architecture}")
    if num_classes < 2:
        raise ModelContractError("num_classes must be >= 2")
    if not 0.0 <= dropout < 1.0:
        raise ModelContractError("dropout must be between 0 and 1")
    weights = MobileNet_V3_Small_Weights.IMAGENET1K_V1 if pretrained else None
    model = mobilenet_v3_small(weights=weights)
    if isinstance(model.classifier[-2], nn.Dropout):
        model.classifier[-2].p = dropout
    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(in_features, num_classes)
    return model


def configure_trainable_stage(
    model: MobileNetV3,
    stage: str,
    unfreeze_last_blocks: int,
) -> ParameterCounts:
    if stage not in {"head", "finetune"}:
        raise ModelContractError(f"Unknown training stage: {stage}")
    if unfreeze_last_blocks < 1:
        raise ModelContractError("unfreeze_last_blocks must be >= 1")

    for parameter in model.parameters():
        parameter.requires_grad = False
    for parameter in model.classifier.parameters():
        parameter.requires_grad = True

    if stage == "finetune":
        if unfreeze_last_blocks > len(model.features):
            raise ModelContractError(
                f"Cannot unfreeze {unfreeze_last_blocks} blocks; "
                f"model has {len(model.features)} feature blocks"
            )
        for block in model.features[-unfreeze_last_blocks:]:
            for parameter in block.parameters():
                parameter.requires_grad = True
    return count_parameters(model)


def set_frozen_batchnorm_eval(model: nn.Module) -> None:
    """Prevent frozen BatchNorm buffers from drifting after model.train()."""

    for module in model.modules():
        if isinstance(module, nn.modules.batchnorm._BatchNorm):
            own_parameters = tuple(module.parameters(recurse=False))
            if own_parameters and not any(item.requires_grad for item in own_parameters):
                module.eval()


def count_parameters(model: nn.Module) -> ParameterCounts:
    total = sum(parameter.numel() for parameter in model.parameters())
    trainable = sum(
        parameter.numel() for parameter in model.parameters() if parameter.requires_grad
    )
    return ParameterCounts(total=total, trainable=trainable)
