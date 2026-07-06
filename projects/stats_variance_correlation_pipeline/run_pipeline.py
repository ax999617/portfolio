from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.analysis import run_analysis
from src.data_processing import clean_analysis_data, write_cleaning_report
from src.pdf_report import build_pdf_report
from src.plotting import generate_figures


PROJECT_ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the variance/correlation statistical analysis pipeline.")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "data" / "example_measurements.csv"))
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "outputs"))
    parser.add_argument("--group-col", default=None)
    parser.add_argument("--metric-col", default=None)
    parser.add_argument("--value-col", default=None)
    parser.add_argument("--sample-col", default=None)
    parser.add_argument("--correlation-method", default="spearman", choices=["pearson", "spearman", "kendall"])
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    figures_dir = output_dir / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    clean_data, cleaning_report = clean_analysis_data(
        args.input,
        group_col=args.group_col,
        metric_col=args.metric_col,
        value_col=args.value_col,
        sample_col=args.sample_col,
    )
    clean_data.to_csv(output_dir / "cleaned_data.csv", index=False, encoding="utf-8-sig")
    write_cleaning_report(cleaning_report, output_dir / "cleaning_report.csv")

    result = run_analysis(clean_data, correlation_method=args.correlation_method)
    result.group_summary.to_csv(output_dir / "group_summary.csv", index=False, encoding="utf-8-sig")
    result.anova_results.to_csv(output_dir / "anova_results.csv", index=False, encoding="utf-8-sig")
    result.correlation_matrix.to_csv(output_dir / "correlation_matrix.csv", encoding="utf-8-sig")

    figures = generate_figures(
        result.group_summary,
        result.anova_results,
        result.correlation_matrix,
        figures_dir,
    )
    source_for_pdf = cleaning_report.source_path.encode("unicode_escape").decode("ascii")
    cleaning_lines = [
        f"Source: {source_for_pdf}",
        f"Rows: original={cleaning_report.original_rows}, cleaned={cleaning_report.cleaned_rows}",
        f"Removed: missing={cleaning_report.missing_rows_removed}, duplicates={cleaning_report.duplicate_rows_removed}",
        f"Groups: {', '.join(cleaning_report.groups)}",
        f"Metrics: {', '.join(cleaning_report.metrics)}",
    ]
    report_pdf = build_pdf_report(
        output_dir / "report.pdf",
        cleaning_lines,
        result.group_summary,
        result.anova_results,
        result.correlation_matrix,
        figures,
    )

    print(
        json.dumps(
            {
                "input": str(Path(args.input)),
                "output_dir": str(output_dir),
                "figures": [str(path) for path in figures],
                "report_pdf": str(report_pdf),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
