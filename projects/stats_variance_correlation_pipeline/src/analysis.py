from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

try:
    from scipy import stats
except Exception:  # pragma: no cover - fallback is for minimal environments.
    stats = None


@dataclass(frozen=True)
class AnalysisResult:
    group_summary: pd.DataFrame
    anova_results: pd.DataFrame
    correlation_matrix: pd.DataFrame


def standard_error(values: pd.Series) -> float:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    if len(clean) <= 1:
        return 0.0
    return float(clean.std(ddof=1) / np.sqrt(len(clean)))


def summarize_by_group(data: pd.DataFrame) -> pd.DataFrame:
    summary = (
        data.groupby(["metric", "group"], as_index=False)
        .agg(
            n=("value", "count"),
            mean=("value", "mean"),
            sd=("value", "std"),
            variance=("value", "var"),
            median=("value", "median"),
        )
    )
    se_values = data.groupby(["metric", "group"])["value"].apply(standard_error).reset_index(name="se")
    return summary.merge(se_values, on=["metric", "group"], how="left")


def one_way_anova(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric, metric_data in data.groupby("metric"):
        groups = [grp["value"].dropna().to_numpy() for _, grp in metric_data.groupby("group")]
        group_count = len(groups)
        sample_count = int(sum(len(values) for values in groups))
        grand_mean = float(metric_data["value"].mean())
        ss_between = sum(len(values) * (float(np.mean(values)) - grand_mean) ** 2 for values in groups if len(values))
        ss_within = sum(float(((values - np.mean(values)) ** 2).sum()) for values in groups if len(values))
        df_between = group_count - 1
        df_within = sample_count - group_count
        ms_between = ss_between / df_between if df_between > 0 else np.nan
        ms_within = ss_within / df_within if df_within > 0 else np.nan
        f_stat = ms_between / ms_within if ms_within and not np.isnan(ms_within) else np.nan
        p_value = np.nan
        if stats is not None and group_count >= 2 and all(len(values) >= 2 for values in groups):
            f_stat, p_value = stats.f_oneway(*groups)
        eta_squared = ss_between / (ss_between + ss_within) if (ss_between + ss_within) else np.nan
        rows.append(
            {
                "metric": metric,
                "groups": group_count,
                "n": sample_count,
                "df_between": df_between,
                "df_within": df_within,
                "f_statistic": float(f_stat) if not np.isnan(f_stat) else np.nan,
                "p_value": float(p_value) if not np.isnan(p_value) else np.nan,
                "eta_squared": float(eta_squared) if not np.isnan(eta_squared) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def correlation_matrix(data: pd.DataFrame, method: str = "spearman") -> pd.DataFrame:
    wide = data.pivot_table(index="sample_id", columns="metric", values="value", aggfunc="mean")
    return wide.corr(method=method)


def run_analysis(data: pd.DataFrame, correlation_method: str = "spearman") -> AnalysisResult:
    return AnalysisResult(
        group_summary=summarize_by_group(data),
        anova_results=one_way_anova(data),
        correlation_matrix=correlation_matrix(data, method=correlation_method),
    )
