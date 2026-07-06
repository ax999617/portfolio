from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def configure_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 180,
            "font.size": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
        }
    )


def plot_group_variance(summary: pd.DataFrame, output_path: str | Path) -> Path:
    configure_style()
    metrics = summary["metric"].drop_duplicates().tolist()
    groups = summary["group"].drop_duplicates().tolist()
    fig, axes = plt.subplots(len(metrics), 1, figsize=(7.5, max(3.0, 2.6 * len(metrics))), squeeze=False)
    palette = ["#4C78A8", "#F58518", "#54A24B", "#B279A2", "#E45756"]

    for axis, metric in zip(axes[:, 0], metrics):
        subset = summary[summary["metric"] == metric].set_index("group").reindex(groups)
        x = np.arange(len(groups))
        axis.bar(
            x,
            subset["mean"].to_numpy(),
            yerr=subset["se"].fillna(0).to_numpy(),
            capsize=4,
            color=[palette[i % len(palette)] for i in range(len(groups))],
            edgecolor="#333333",
            linewidth=0.8,
        )
        axis.set_title(f"{metric}: group mean +/- SE")
        axis.set_ylabel("value")
        axis.set_xticks(x, groups, rotation=20, ha="right")

    fig.tight_layout()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_correlation_heatmap(correlation: pd.DataFrame, output_path: str | Path) -> Path:
    configure_style()
    fig, axis = plt.subplots(figsize=(6.8, 5.8))
    values = correlation.to_numpy(dtype=float)
    image = axis.imshow(values, vmin=-1, vmax=1, cmap="coolwarm")
    axis.set_title("Metric correlation matrix")
    axis.set_xticks(np.arange(len(correlation.columns)), correlation.columns, rotation=35, ha="right")
    axis.set_yticks(np.arange(len(correlation.index)), correlation.index)
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            axis.text(j, i, f"{values[i, j]:.2f}", ha="center", va="center", color="#1f1f1f", fontsize=8)
    fig.colorbar(image, ax=axis, fraction=0.046, pad=0.04, label="correlation")
    fig.tight_layout()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_anova_effects(anova_results: pd.DataFrame, output_path: str | Path) -> Path:
    configure_style()
    ordered = anova_results.sort_values("eta_squared", ascending=False)
    fig, axis = plt.subplots(figsize=(7.5, 4.2))
    axis.barh(ordered["metric"], ordered["eta_squared"], color="#72B7B2", edgecolor="#333333", linewidth=0.8)
    axis.invert_yaxis()
    axis.set_xlabel("eta squared")
    axis.set_title("One-way ANOVA effect size by metric")
    for y_pos, value in enumerate(ordered["eta_squared"]):
        if pd.notna(value):
            axis.text(value + 0.01, y_pos, f"{value:.2f}", va="center", fontsize=8)
    fig.tight_layout()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def generate_figures(summary: pd.DataFrame, anova_results: pd.DataFrame, correlation: pd.DataFrame, figures_dir: str | Path) -> list[Path]:
    out_dir = Path(figures_dir)
    return [
        plot_group_variance(summary, out_dir / "group_mean_se.png"),
        plot_anova_effects(anova_results, out_dir / "anova_effect_sizes.png"),
        plot_correlation_heatmap(correlation, out_dir / "correlation_heatmap.png"),
    ]
