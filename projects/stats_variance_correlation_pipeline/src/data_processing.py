from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


GROUP_CANDIDATES = ("group", "treatment", "condition", "处理", "分组", "组别")
METRIC_CANDIDATES = ("metric", "indicator", "variable", "指标", "变量")
VALUE_CANDIDATES = ("value", "measurement", "mean", "数值", "测量值")
SAMPLE_CANDIDATES = ("sample_id", "sample", "id", "样本", "样本编号")


@dataclass(frozen=True)
class CleaningReport:
    source_path: str
    original_rows: int
    cleaned_rows: int
    duplicate_rows_removed: int
    missing_rows_removed: int
    metrics: list[str]
    groups: list[str]


def normalize_column_name(name: object) -> str:
    text = str(name).strip().lower()
    text = re.sub(r"[\s\-\/]+", "_", text)
    text = re.sub(r"[^\w\u4e00-\u9fff]+", "", text)
    return text


def read_table(path: str | Path) -> pd.DataFrame:
    table_path = Path(path)
    suffix = table_path.suffix.lower()
    if suffix in {".xlsx", ".xls", ".xlsm"}:
        return pd.read_excel(table_path)
    if suffix == ".tsv":
        return pd.read_csv(table_path, sep="\t")
    return pd.read_csv(table_path)


def find_column(columns: Iterable[str], candidates: Iterable[str]) -> str | None:
    normalized = {normalize_column_name(col): col for col in columns}
    for candidate in candidates:
        key = normalize_column_name(candidate)
        if key in normalized:
            return normalized[key]
    return None


def standardize_long_table(
    raw: pd.DataFrame,
    group_col: str | None = None,
    metric_col: str | None = None,
    value_col: str | None = None,
    sample_col: str | None = None,
) -> pd.DataFrame:
    data = raw.copy()
    data.columns = [normalize_column_name(col) for col in data.columns]

    group_col = normalize_column_name(group_col) if group_col else find_column(data.columns, GROUP_CANDIDATES)
    metric_col = normalize_column_name(metric_col) if metric_col else find_column(data.columns, METRIC_CANDIDATES)
    value_col = normalize_column_name(value_col) if value_col else find_column(data.columns, VALUE_CANDIDATES)
    sample_col = normalize_column_name(sample_col) if sample_col else find_column(data.columns, SAMPLE_CANDIDATES)

    if group_col and metric_col and value_col:
        sample_col = sample_col or "__row_id"
        if sample_col == "__row_id":
            data[sample_col] = [f"sample_{idx + 1:03d}" for idx in range(len(data))]
        out = data[[sample_col, group_col, metric_col, value_col]].rename(
            columns={sample_col: "sample_id", group_col: "group", metric_col: "metric", value_col: "value"}
        )
        return out

    if not group_col:
        raise ValueError("Could not infer a grouping column. Pass --group-col explicitly.")

    id_cols = [group_col]
    if sample_col:
        id_cols.insert(0, sample_col)
    else:
        data["sample_id"] = [f"sample_{idx + 1:03d}" for idx in range(len(data))]
        id_cols.insert(0, "sample_id")

    numeric_cols = [
        col for col in data.columns
        if col not in set(id_cols) and pd.api.types.is_numeric_dtype(pd.to_numeric(data[col], errors="coerce"))
    ]
    if not numeric_cols:
        raise ValueError("Could not infer numeric measurement columns for wide-to-long conversion.")

    out = data.melt(id_vars=id_cols, value_vars=numeric_cols, var_name="metric", value_name="value")
    return out.rename(columns={group_col: "group", id_cols[0]: "sample_id"})


def clean_analysis_data(
    path: str | Path,
    group_col: str | None = None,
    metric_col: str | None = None,
    value_col: str | None = None,
    sample_col: str | None = None,
) -> tuple[pd.DataFrame, CleaningReport]:
    raw = read_table(path)
    long_data = standardize_long_table(raw, group_col, metric_col, value_col, sample_col)
    long_data["group"] = long_data["group"].astype(str).str.strip()
    long_data["metric"] = long_data["metric"].astype(str).str.strip()
    long_data["sample_id"] = long_data["sample_id"].astype(str).str.strip()
    long_data["value"] = pd.to_numeric(long_data["value"], errors="coerce")

    before_missing = len(long_data)
    long_data = long_data.dropna(subset=["sample_id", "group", "metric", "value"])
    missing_removed = before_missing - len(long_data)

    before_dupes = len(long_data)
    long_data = long_data.drop_duplicates(subset=["sample_id", "group", "metric"], keep="first")
    duplicate_removed = before_dupes - len(long_data)

    long_data = long_data.sort_values(["metric", "group", "sample_id"]).reset_index(drop=True)
    report = CleaningReport(
        source_path=str(Path(path)),
        original_rows=len(raw),
        cleaned_rows=len(long_data),
        duplicate_rows_removed=duplicate_removed,
        missing_rows_removed=missing_removed,
        metrics=sorted(long_data["metric"].unique().tolist()),
        groups=sorted(long_data["group"].unique().tolist()),
    )
    return long_data, report


def write_cleaning_report(report: CleaningReport, output_path: str | Path) -> None:
    out = pd.DataFrame(
        [
            {"field": "source_path", "value": report.source_path},
            {"field": "original_rows", "value": report.original_rows},
            {"field": "cleaned_rows", "value": report.cleaned_rows},
            {"field": "duplicate_rows_removed", "value": report.duplicate_rows_removed},
            {"field": "missing_rows_removed", "value": report.missing_rows_removed},
            {"field": "metrics", "value": ", ".join(report.metrics)},
            {"field": "groups", "value": ", ".join(report.groups)},
        ]
    )
    out.to_csv(output_path, index=False, encoding="utf-8-sig")
