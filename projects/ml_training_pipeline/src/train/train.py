from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

import sys

SRC_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC_ROOT))

from models.trained import TrainedHenanModel


DEFAULT_CLASSES = [
    "luoyang_peony",
    "zhengzhou_bronze_artifact",
    "xinyang_maojian_tea_plant",
]


def build_transform() -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Train the refactored 3-class image classifier.")
    parser.add_argument("--data-dir", required=True, help="ImageFolder dataset root.")
    parser.add_argument("--output", default="artifacts/weights/retrained.pth")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    args = parser.parse_args()

    dataset = datasets.ImageFolder(args.data_dir, transform=build_transform())
    if len(dataset.classes) != 3:
        raise ValueError(f"Expected 3 classes, found {len(dataset.classes)}: {dataset.classes}")

    val_size = max(1, int(len(dataset) * args.val_ratio))
    train_size = len(dataset) - val_size
    train_set, val_set = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=args.batch_size)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TrainedHenanModel(num_classes=3).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    history = []
    for epoch in range(args.epochs):
        model.train()
        total_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()
            total_loss += float(loss.item())

        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                preds = model(images).argmax(dim=1)
                correct += int((preds == labels).sum().item())
                total += int(labels.numel())

        item = {
            "epoch": epoch + 1,
            "train_loss": total_loss / max(1, len(train_loader)),
            "val_accuracy": correct / max(1, total),
        }
        history.append(item)
        print(json.dumps(item, ensure_ascii=False))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
