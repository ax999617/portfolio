# Statistical Assets: Read-only Gate

## Purpose

The historical statistics entrypoint writes tracked catalogs, previews, and reports. This gate therefore checks only the presence of named source snapshots, frozen reference assets, and known write targets. It does not import the legacy pipeline, open CSV contents, calculate statistics, recompute CLD, or render figures.

## Run the safe checks

From the repository root:

```powershell
python projects/stats_variance_correlation_pipeline_test_v1/check_plan_test_v1.py --strict
python -m unittest discover -s projects/stats_variance_correlation_pipeline_test_v1/tests -p "test*_test_v1.py" -v
```

The command writes JSON to stdout only. `required_files_present=true` means the 4 named CSV paths and 3 frozen assets exist; it does **not** validate file contents, analysis completeness, or scientific conclusions.

## Safety boundary

- `safe_to_run_legacy` remains deliberately `false`.
- CSV values are never opened by this gate.
- No output directory or report is created.
- Any future regeneration must use a separate writable copy and a separately reviewed output plan.

## Provenance and source CSV / 溯源与来源 CSV

- Repository: `D:\工作流\portfolio`
- Historical module: `D:\工作流\portfolio\projects\stats_variance_correlation_pipeline`
- Original source root: `D:\项目文件202605\制图数据`
- Source CSV / 来源 CSV:
  - `D:\项目文件202605\制图数据\data\clean\soil_core_variables_latest_long.csv`
  - `D:\项目文件202605\制图数据\data\clean\soil_core_variables_latest_v3_long.csv`
  - `D:\项目文件202605\制图数据\data\clean\soil_physicochemical_latest_v3_wide.csv`
  - `D:\项目文件202605\制图数据\data\clean\soil_physicochemical_latest_wide.csv`
- This gate does not modify CSV, Excel, manifest, statistics, CLD, PDF, preview, or frozen figure files.
