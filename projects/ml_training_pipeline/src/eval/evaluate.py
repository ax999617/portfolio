from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

import sys

SRC_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC_ROOT))

from models.trained import TrainedHenanModel


def build_transform() -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
            )


def load_model(weights: str, device: torch.device) -> torch.nn.Module:
    checkpoint = torch.load(weights, map_location=device)
    if isinstance(checkpoint, torch.nn.Module):
        return checkpoint.to(device).eval()

    model = TrainedHenanModel(num_classes=3).to(device)
    state = checkpoint.get("model_state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint
    model.load_state_dict(state, strict=False)
    return model.eval()


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate the refactored classifier.")
    parser.add_argument("--data-dir", required=True, help="ImageFolder dataset root.")
    parser.add_argument("--weights", default="artifacts/weights/trained.pth")
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()

    dataset = datasets.ImageFolder(args.data_dir, transform=build_transform())
    loader = DataLoader(dataset, batch_size=args.batch_size)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(args.weights, device)

    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            preds = model(images).argmax(dim=1)
            correct += int((preds == labels).sum().item())
            total += int(labels.numel())

    print(json.dumps({"samples": total, "accuracy": correct / max(1, total)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
