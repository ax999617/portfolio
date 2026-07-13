from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader


V2_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(V2_ROOT / "src"))

from henan_v2.checkpoint import CheckpointError, load_checkpoint, restore_model  # noqa: E402
from henan_v2.data import DataContractError, build_contract_dataset  # noqa: E402
from henan_v2.engine import TrainingError, resolve_device, run_epoch  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Strictly evaluate a v2 checkpoint.")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--split", choices=("val", "test"), default="test")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument(
        "--device", choices=("auto", "cpu", "cuda", "mps"), default="auto"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.batch_size < 1 or args.num_workers < 0:
        raise ValueError("batch-size must be >= 1 and num-workers must be >= 0")
    checkpoint = load_checkpoint(args.checkpoint)
    device = resolve_device(args.device)
    model = restore_model(checkpoint, device).eval()
    class_to_idx = checkpoint["class_to_idx"]
    class_names = [
        name for name, _ in sorted(class_to_idx.items(), key=lambda item: item[1])
    ]
    dataset = build_contract_dataset(
        args.data_root / args.split,
        class_names,
        checkpoint["preprocessing"],
    )
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=device.type == "cuda",
        persistent_workers=args.num_workers > 0,
    )
    metrics = run_epoch(
        model=model,
        loader=loader,
        criterion=nn.CrossEntropyLoss(),
        device=device,
        num_classes=len(class_names),
    )
    result = {
        "checkpoint": str(args.checkpoint),
        "split": args.split,
        "class_to_idx": class_to_idx,
        "metrics": metrics,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CheckpointError, DataContractError, TrainingError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
