from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 180,
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.22,
        }
    )


def plot_group_means(summary: pd.DataFrame, output_path: Path) -> Path:
    _style()
    metrics = summary["metric"].drop_duplicates().tolist()
    groups = summary["group"].drop_duplicates().tolist()
    fig, axes = plt.subplots(len(metrics), 1, figsize=(7.2, max(3.0, 2.4 * len(metrics))), squeeze=False)
    colors = ["#2f6f73", "#8a5a44", "#5f6f52", "#9b5de5", "#d1495b"]
    for axis, metric in zip(axes[:, 0], metrics):
        subset = summary[summary["metric"] == metric].set_index("group").reindex(groups)
        x = np.arange(len(groups))
        axis.bar(
            x,
            subset["mean"].to_numpy(),
            yerr=subset["se"].fillna(0).to_numpy(),
            capsize=4,
            color=[colors[index % len(colors)] for index in range(len(groups))],
            edgecolor="#222222",
            linewidth=0.6,
        )
        axis.set_title(f"{metric}: group mean +/- SE")
        axis.set_ylabel("value")
        axis.set_xticks(x, groups, rotation=25, ha="right")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_correlation_heatmap(correlation: pd.DataFrame, output_path: Path) -> Path:
    _style()
    fig, axis = plt.subplots(figsize=(6.4, 5.4))
    values = correlation.to_numpy(dtype=float)
    image = axis.imshow(values, vmin=-1, vmax=1, cmap="vlag" if "vlag" in plt.colormaps() else "coolwarm")
    axis.set_title("Correlation matrix")
    axis.set_xticks(np.arange(len(correlation.columns)), correlation.columns, rotation=35, ha="right")
    axis.set_yticks(np.arange(len(correlation.index)), correlation.index)
    for row in range(values.shape[0]):
        for col in range(values.shape[1]):
            value = values[row, col]
            axis.text(col, row, "" if pd.isna(value) else f"{value:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return output_path
