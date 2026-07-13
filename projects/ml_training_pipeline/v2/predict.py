from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from PIL import Image, ImageOps


V2_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(V2_ROOT / "src"))

from henan_v2.checkpoint import CheckpointError, load_checkpoint, restore_model  # noqa: E402
from henan_v2.data import DataContractError, build_eval_transform  # noqa: E402
from henan_v2.engine import TrainingError, resolve_device  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run strict v2 single-image inference.")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument(
        "--device", choices=("auto", "cpu", "cuda", "mps"), default="auto"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checkpoint = load_checkpoint(args.checkpoint)
    device = resolve_device(args.device)
    model = restore_model(checkpoint, device).eval()
    class_to_idx = checkpoint["class_to_idx"]
    if not 1 <= args.top_k <= len(class_to_idx):
        raise ValueError(f"top-k must be between 1 and {len(class_to_idx)}")
    preprocessing = checkpoint["preprocessing"]
    transform = build_eval_transform(
        int(preprocessing["image_size"]),
        int(preprocessing["resize_size"]),
        preprocessing["normalization_mean"],
        preprocessing["normalization_std"],
    )
    with Image.open(args.image) as raw_image:
        image = ImageOps.exif_transpose(raw_image).convert("RGB")
        tensor = transform(image).unsqueeze(0).to(device)
    with torch.inference_mode():
        probabilities = torch.softmax(model(tensor), dim=1)[0]
    scores, indices = torch.topk(probabilities, k=args.top_k)
    idx_to_class = {index: name for name, index in class_to_idx.items()}
    display_names = checkpoint["display_names"]
    predictions = [
        {
            "class": idx_to_class[int(index)],
            "display_name": display_names[idx_to_class[int(index)]],
            "confidence": float(score),
        }
        for score, index in zip(scores.cpu(), indices.cpu())
    ]
    result = {
        "image": str(args.image),
        "checkpoint": str(args.checkpoint),
        "predictions": predictions,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CheckpointError, DataContractError, TrainingError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
