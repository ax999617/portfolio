from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(V2_ROOT / "src"))

from henan_v2.audit import audit_dataset  # noqa: E402
from henan_v2.config import ConfigError, load_config  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit dataset readiness without training or modifying source files."
    )
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument(
        "--config",
        type=Path,
        default=V2_ROOT / "configs" / "train.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path; stdout is used when omitted.",
    )
    parser.add_argument(
        "--require-training-ready",
        action="store_true",
        help="Return a non-zero exit code unless prepared train/val data passes.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    report = audit_dataset(args.data_root, config)
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    if report["layout"] == "missing":
        return 2
    if args.require_training_ready and not report["training_ready"]:
        return 3
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ConfigError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
