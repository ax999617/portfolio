from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms

import sys

SRC_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC_ROOT))

from models.trained import TrainedHenanModel


CLASS_NAMES = [
    "luoyang_peony",
    "zhengzhou_bronze_artifact",
    "xinyang_maojian_tea_plant",
]


def load_model(weights: str, device: torch.device) -> torch.nn.Module:
    checkpoint = torch.load(weights, map_location=device)
    if isinstance(checkpoint, torch.nn.Module):
        return checkpoint.to(device).eval()

    model = TrainedHenanModel(num_classes=3).to(device)
    state = checkpoint.get("model_state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint
    model.load_state_dict(state, strict=False)
    return model.eval()


def build_transform() -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run single-image inference.")
    parser.add_argument("--image", required=True)
    parser.add_argument("--weights", default="artifacts/weights/trained.pth")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(args.weights, device)

    image = Image.open(args.image).convert("RGB")
    tensor = build_transform()(image).unsqueeze(0).to(device)
    with torch.no_grad():
        probs = torch.softmax(model(tensor), dim=1)[0]
    top = torch.topk(probs, k=min(3, len(CLASS_NAMES)))

    result = [
        {"class": CLASS_NAMES[int(idx)], "confidence": float(score)}
        for score, idx in zip(top.values.cpu(), top.indices.cpu())
    ]
    print(json.dumps({"image": str(Path(args.image)), "predictions": result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
