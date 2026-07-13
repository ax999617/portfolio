# Provenance Record and Update History

This page preserves the reason earlier documentation was revised. The first portfolio overview predated both the statistical module and ML pipeline v2, so statements such as “no source CSV identified” were valid only for the original CV/ML/ComfyUI asset sets, not for the repository as a whole.

## Current record

- The statistical module contains four committed clean CSV snapshots.
- ML v2 records a machine-local three-class source audit, while correctly keeping `training_ready=false` until provenance-aware train/validation/test grouping exists.
- `projects/ml_training_pipeline/v2/` is the current ML path; parent-directory weights remain `legacy/unverified`.
- The historical statistical entrypoint writes tracked outputs and is not the supported review path.
- The visitor-facing `dataset_notes.md`, `methodology.md`, and `system_overview.md` now state these boundaries directly.

## Source CSV

Original root: `D:\项目文件202605\制图数据`

- `data\clean\soil_core_variables_latest_long.csv`
- `data\clean\soil_core_variables_latest_v3_long.csv`
- `data\clean\soil_physicochemical_latest_v3_wide.csv`
- `data\clean\soil_physicochemical_latest_wide.csv`

The committed copies are under `projects/stats_variance_correlation_pipeline/data/clean/`. This update records paths only and does not read or modify their values.

## Provenance boundary

- Repository root: `D:\工作流\portfolio`
- Original correction baseline: `a5a8e4012bc0a91d1d1eb81ce79d2605f0c6f186`
- Detailed statistical mapping remains in `projects/stats_variance_correlation_pipeline/source_asset_inventory.md`.
- No CSV, Excel, manifest, statistic, CLD, historical report, or frozen figure was modified.
