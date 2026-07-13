from __future__ import annotations

from dataclasses import dataclass, field

import torch


@dataclass
class ClassificationMeter:
    num_classes: int
    loss_sum: float = 0.0
    sample_count: int = 0
    confusion: torch.Tensor = field(init=False)

    def __post_init__(self) -> None:
        if self.num_classes < 2:
            raise ValueError("num_classes must be >= 2")
        self.confusion = torch.zeros(
            (self.num_classes, self.num_classes), dtype=torch.int64
        )

    def update(self, logits: torch.Tensor, targets: torch.Tensor, loss: float) -> None:
        if logits.ndim != 2 or logits.shape[1] != self.num_classes:
            raise ValueError("logits do not match num_classes")
        targets = targets.detach().to(device="cpu", dtype=torch.int64)
        predictions = logits.detach().argmax(dim=1).to(device="cpu", dtype=torch.int64)
        if predictions.shape != targets.shape:
            raise ValueError("predictions and targets have different shapes")
        batch_size = int(targets.numel())
        self.loss_sum += float(loss) * batch_size
        self.sample_count += batch_size
        encoded = targets * self.num_classes + predictions
        self.confusion += torch.bincount(
            encoded, minlength=self.num_classes**2
        ).reshape(self.num_classes, self.num_classes)

    def compute(self) -> dict[str, object]:
        if self.sample_count == 0:
            raise ValueError("Cannot compute metrics for an empty loader")
        true_positive = self.confusion.diag().to(torch.float64)
        false_positive = self.confusion.sum(dim=0).to(torch.float64) - true_positive
        false_negative = self.confusion.sum(dim=1).to(torch.float64) - true_positive
        denominator = 2 * true_positive + false_positive + false_negative
        class_f1 = torch.where(
            denominator > 0,
            2 * true_positive / denominator,
            torch.zeros_like(denominator),
        )
        accuracy = float(true_positive.sum().item() / self.sample_count)
        return {
            "loss": self.loss_sum / self.sample_count,
            "accuracy": accuracy,
            "macro_f1": float(class_f1.mean().item()),
            "samples": self.sample_count,
            "confusion_matrix": self.confusion.tolist(),
        }
