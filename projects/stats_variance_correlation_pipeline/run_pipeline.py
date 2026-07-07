from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.assets import package_result_assets, write_source_catalog
from src.catalog import DEFAULT_SOURCE_ROOT
from src.report import build_package_report
from src.table_methods import run_optional_analysis


PROJECT_ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Package source-derived statistical result assets and optional new-data analysis outputs."
    )
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT), help="Historical source root to prefer when available.")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "outputs"), help="Pipeline output directory.")
    parser.add_argument("--skip-render", action="store_true", help="Copy assets but skip PDF-to-PNG preview rendering.")
    parser.add_argument(
        "--refresh-reference-assets",
        action="store_true",
        help="Refresh committed reference assets from the local source root when it exists.",
    )
    parser.add_argument("--analysis-input", default=None, help="Optional new CSV/TSV/XLSX table for reusable analysis methods.")
    parser.add_argument("--group-col", default=None, help="Group/treatment column for optional analysis.")
    parser.add_argument("--sample-col", default=None, help="Sample id column for optional analysis.")
    parser.add_argument("--metric-col", default=None, help="Metric column for optional long-format analysis.")
    parser.add_argument("--value-col", default=None, help="Value column for optional long-format analysis.")
    parser.add_argument(
        "--correlation-method",
        default="spearman",
        choices=("pearson", "spearman", "kendall"),
        help="Correlation method for optional analysis.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    catalog_path = write_source_catalog(PROJECT_ROOT / "data" / "source_asset_catalog.json")
    package_summary = package_result_assets(
        source_root=Path(args.source_root),
        project_root=PROJECT_ROOT,
        output_dir=output_dir,
        render_previews=not args.skip_render,
        refresh_reference_assets=args.refresh_reference_assets,
    )

    optional_analysis = None
    if args.analysis_input:
        optional_analysis = run_optional_analysis(
            input_path=Path(args.analysis_input),
            output_dir=output_dir / "optional_analysis",
            group_col=args.group_col,
            sample_col=args.sample_col,
            metric_col=args.metric_col,
            value_col=args.value_col,
            correlation_method=args.correlation_method,
        )

    report_path = build_package_report(
        output_pdf=output_dir / "report.pdf",
        package_summary=package_summary,
        optional_analysis=optional_analysis,
    )

    result = {
        "catalog": str(catalog_path),
        "summary": str(output_dir / "asset_package_summary.json"),
        "report_pdf": str(report_path),
        "result_assets": package_summary["outputs"],
        "optional_analysis": optional_analysis,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
