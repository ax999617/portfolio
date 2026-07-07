from __future__ import annotations

from pathlib import Path

import pandas as pd

from .visualization import plot_correlation_heatmap, plot_group_means


def read_table(input_path: Path) -> pd.DataFrame:
    suffix = input_path.suffix.lower()
    if suffix in {".xlsx", ".xls", ".xlsm"}:
        return pd.read_excel(input_path)
    if suffix == ".tsv":
        return pd.read_csv(input_path, sep="\t")
    return pd.read_csv(input_path)


def standardize_table(
    raw: pd.DataFrame,
    group_col: str | None = None,
    sample_col: str | None = None,
    metric_col: str | None = None,
    value_col: str | None = None,
) -> pd.DataFrame:
    data = raw.copy()
    data.columns = [str(col).strip() for col in data.columns]
    group_col = group_col or _first_existing(data, ("group", "treatment", "condition"))
    sample_col = sample_col or _first_existing(data, ("sample_id", "sample", "id"))
    metric_col = metric_col or _first_existing(data, ("metric", "indicator", "variable"))
    value_col = value_col or _first_existing(data, ("value", "measurement"))

    if group_col is None:
        raise ValueError("A group/treatment column is required for optional analysis.")

    if metric_col and value_col:
        sample_col = sample_col or "_row_id"
        if sample_col == "_row_id":
            data[sample_col] = [f"sample_{idx + 1:03d}" for idx in range(len(data))]
        long_data = data[[sample_col, group_col, metric_col, value_col]].rename(
            columns={sample_col: "sample_id", group_col: "group", metric_col: "metric", value_col: "value"}
        )
    else:
        sample_col = sample_col or "_row_id"
        if sample_col == "_row_id":
            data[sample_col] = [f"sample_{idx + 1:03d}" for idx in range(len(data))]
        numeric_columns = [
            col
            for col in data.columns
            if col not in {sample_col, group_col}
            and pd.to_numeric(data[col], errors="coerce").notna().any()
        ]
        if not numeric_columns:
            raise ValueError("No numeric measurement columns found for optional analysis.")
        long_data = data.melt(
            id_vars=[sample_col, group_col],
            value_vars=numeric_columns,
            var_name="metric",
            value_name="value",
        ).rename(columns={sample_col: "sample_id", group_col: "group"})

    long_data["sample_id"] = long_data["sample_id"].astype(str).str.strip()
    long_data["group"] = long_data["group"].astype(str).str.strip()
    long_data["metric"] = long_data["metric"].astype(str).str.strip()
    long_data["value"] = pd.to_numeric(long_data["value"], errors="coerce")
    long_data = long_data.dropna(subset=["sample_id", "group", "metric", "value"])
    long_data = long_data.drop_duplicates(subset=["sample_id", "group", "metric"], keep="first")
    return long_data.sort_values(["metric", "group", "sample_id"]).reset_index(drop=True)


def _first_existing(data: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    lower_to_original = {str(col).lower(): str(col) for col in data.columns}
    for candidate in candidates:
        if candidate.lower() in lower_to_original:
            return lower_to_original[candidate.lower()]
    return None


def group_summary(clean_data: pd.DataFrame) -> pd.DataFrame:
    grouped = clean_data.groupby(["metric", "group"], as_index=False)["value"]
    out = grouped.agg(n="count", mean="mean", sd="std", variance="var", median="median")
    out["se"] = out["sd"] / (out["n"] ** 0.5)
    return out


def variance_components(clean_data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric, metric_data in clean_data.groupby("metric"):
        groups = [grp["value"].to_numpy() for _, grp in metric_data.groupby("group")]
        grand_mean = metric_data["value"].mean()
        ss_between = sum(len(values) * (values.mean() - grand_mean) ** 2 for values in groups if len(values))
        ss_within = sum(((values - values.mean()) ** 2).sum() for values in groups if len(values))
        df_between = len(groups) - 1
        df_within = len(metric_data) - len(groups)
        ms_between = ss_between / df_between if df_between > 0 else pd.NA
        ms_within = ss_within / df_within if df_within > 0 else pd.NA
        f_statistic = ms_between / ms_within if ms_within is not pd.NA and ms_within != 0 else pd.NA
        eta_squared = ss_between / (ss_between + ss_within) if (ss_between + ss_within) else pd.NA
        rows.append(
            {
                "metric": metric,
                "groups": len(groups),
                "n": len(metric_data),
                "df_between": df_between,
                "df_within": df_within,
                "ss_between": ss_between,
                "ss_within": ss_within,
                "f_statistic": f_statistic,
                "eta_squared": eta_squared,
            }
        )
    return pd.DataFrame(rows)


def correlation_matrix(clean_data: pd.DataFrame, method: str = "spearman") -> pd.DataFrame:
    wide = clean_data.pivot_table(index="sample_id", columns="metric", values="value", aggfunc="mean")
    return wide.corr(method=method)


def run_optional_analysis(
    input_path: Path,
    output_dir: Path,
    group_col: str | None = None,
    sample_col: str | None = None,
    metric_col: str | None = None,
    value_col: str | None = None,
    correlation_method: str = "spearman",
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw = read_table(input_path)
    clean_data = standardize_table(raw, group_col, sample_col, metric_col, value_col)
    summary = group_summary(clean_data)
    variance = variance_components(clean_data)
    correlation = correlation_matrix(clean_data, method=correlation_method)

    clean_path = output_dir / "cleaned_long_table.csv"
    summary_path = output_dir / "group_summary.csv"
    variance_path = output_dir / "variance_components.csv"
    correlation_path = output_dir / "correlation_matrix.csv"
    clean_data.to_csv(clean_path, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    variance.to_csv(variance_path, index=False, encoding="utf-8-sig")
    correlation.to_csv(correlation_path, encoding="utf-8-sig")

    figure_dir = output_dir / "figures"
    figures = [
        plot_group_means(summary, figure_dir / "group_means.png"),
        plot_correlation_heatmap(correlation, figure_dir / "correlation_heatmap.png"),
    ]
    return {
        "input_path": str(input_path),
        "outputs": [str(clean_path), str(summary_path), str(variance_path), str(correlation_path), *map(str, figures)],
    }
