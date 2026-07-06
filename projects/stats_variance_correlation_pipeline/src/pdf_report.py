from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages


def _text_page(title: str, lines: list[str]):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.text(0.08, 0.94, title, fontsize=18, weight="bold", va="top")
    y = 0.88
    for line in lines:
        fig.text(0.08, y, line, fontsize=10, va="top")
        y -= 0.035
        if y < 0.08:
            break
    return fig


def _table_page(title: str, table: pd.DataFrame, max_rows: int = 16):
    fig, axis = plt.subplots(figsize=(11.69, 8.27))
    axis.axis("off")
    axis.set_title(title, loc="left", fontsize=14, weight="bold")
    display = table.head(max_rows).copy()
    for col in display.columns:
        if pd.api.types.is_numeric_dtype(display[col]):
            display[col] = display[col].map(lambda x: "" if pd.isna(x) else f"{x:.4g}")
    mpl_table = axis.table(
        cellText=display.astype(str).values,
        colLabels=display.columns,
        loc="center",
        cellLoc="center",
    )
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(8)
    mpl_table.scale(1, 1.35)
    return fig


def build_pdf_report(
    output_pdf: str | Path,
    cleaning_lines: list[str],
    summary: pd.DataFrame,
    anova_results: pd.DataFrame,
    correlation: pd.DataFrame,
    figure_paths: list[Path],
) -> Path:
    out = Path(output_pdf)
    out.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out) as pdf:
        cover = _text_page(
            "Variance and Correlation Analysis Report",
            [
                "Pipeline outputs are generated from the selected input table.",
                "The report includes data-cleaning notes, group summaries, ANOVA effect sizes, and a correlation matrix.",
                "",
                *cleaning_lines,
            ],
        )
        pdf.savefig(cover, bbox_inches="tight")
        plt.close(cover)

        pdf.savefig(_table_page("Group summary", summary), bbox_inches="tight")
        plt.close()
        pdf.savefig(_table_page("One-way ANOVA results", anova_results), bbox_inches="tight")
        plt.close()
        pdf.savefig(_table_page("Correlation matrix", correlation.reset_index().rename(columns={"index": "metric"})), bbox_inches="tight")
        plt.close()

        for figure_path in figure_paths:
            image = plt.imread(figure_path)
            fig, axis = plt.subplots(figsize=(11.69, 8.27))
            axis.imshow(image)
            axis.axis("off")
            axis.set_title(figure_path.name, loc="left")
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)
    return out
