# Stats Pipeline Read-only Gate - test v1

## Purpose

The legacy statistics entrypoint writes tracked catalogs, previews, and reports. This versioned gate therefore performs presence and write-boundary checks only. It does not import or call the legacy pipeline, open CSV contents, calculate statistics, recompute CLD, or render figures.

## Check

From the repository root:

```powershell
python projects/stats_variance_correlation_pipeline_test_v1/check_plan_test_v1.py --strict
python -m unittest discover -s projects/stats_variance_correlation_pipeline_test_v1/tests -p "test*_test_v1.py" -v
```

The command writes JSON to stdout only. It lists whether expected source copies and frozen assets exist and records which legacy targets would be unsafe to overwrite.

## Boundary

- `safe_to_run_legacy` is deliberately `false`.
- File existence is checked without reading CSV values.
- No output directory is created.
- To regenerate or analyze anything later, use a separate writable copy and obtain explicit approval first.

## Provenance and source CSV / 溯源与来源 CSV

- Test repository: `D:\工作流\portfolio`
- Legacy module: `D:\工作流\portfolio\projects\stats_variance_correlation_pipeline`
- Original source root: `D:\项目文件202605\制图数据`
- Source CSV:
  - `D:\项目文件202605\制图数据\data\clean\soil_core_variables_latest_long.csv`
  - `D:\项目文件202605\制图数据\data\clean\soil_core_variables_latest_v3_long.csv`
  - `D:\项目文件202605\制图数据\data\clean\soil_physicochemical_latest_v3_wide.csv`
  - `D:\项目文件202605\制图数据\data\clean\soil_physicochemical_latest_wide.csv`
- No CSV, Excel, manifest, statistic, CLD, PDF, preview, or frozen figure is modified by this test-v1 gate.
