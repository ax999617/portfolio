from __future__ import annotations

import argparse
import json
from pathlib import Path


LEGACY_ROOT = Path(__file__).resolve().parent.parent / "stats_variance_correlation_pipeline"
EXPECTED_CSV = (
    "data/clean/soil_core_variables_latest_long.csv",
    "data/clean/soil_core_variables_latest_v3_long.csv",
    "data/clean/soil_physicochemical_latest_v3_wide.csv",
    "data/clean/soil_physicochemical_latest_wide.csv",
)
FROZEN_ASSETS = (
    "reference_results/original/Fig_NH4N_methodB2v2_01.pdf",
    "reference_results/original/Fig_NO3N_methodB2v2_01.pdf",
    "reference_results/original/SPSS_NO3-N.png",
)
LEGACY_WRITE_TARGETS = (
    "data/source_asset_catalog.json",
    "outputs/asset_package_summary.json",
    "outputs/report.pdf",
    "outputs/result_assets/previews",
)


def build_read_only_plan(project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    source_csv = [
        {"path": relative, "exists": (root / relative).is_file()} for relative in EXPECTED_CSV
    ]
    frozen_assets = [
        {"path": relative, "exists": (root / relative).is_file()} for relative in FROZEN_ASSETS
    ]
    write_targets = [
        {"path": relative, "exists": (root / relative).exists()} for relative in LEGACY_WRITE_TARGETS
    ]
    return {
        "contract_version": "test-v1",
        "project_root": str(root),
        "read_only": True,
        "safe_to_run_legacy": False,
        "source_csv": source_csv,
        "frozen_assets": frozen_assets,
        "blocked_legacy_write_targets": write_targets,
        "required_files_present": all(item["exists"] for item in source_csv + frozen_assets),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check stats source presence without opening data or writing outputs.")
    parser.add_argument("--project-root", default=str(LEGACY_ROOT))
    parser.add_argument("--strict", action="store_true", help="Return exit code 2 when required files are missing.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = build_read_only_plan(args.project_root)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 2 if args.strict and not plan["required_files_present"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
