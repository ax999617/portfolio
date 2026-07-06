# Source Asset Inventory

Source provenance:

- Scanned root: `D:\项目文件202605`
- Primary project root found during scan: `D:\项目文件202605\制图数据`
- Source CSV copied into this module: none
- New reproducible demo CSV: `data/example_measurements.csv`

## Effective Historical Assets Identified

The scan found 32,778 files, including 1,198 keyword candidates and 316 CSV/Excel-like data files. Third-party R packages under `r_libs`, NEWS files, temporary/test paths, and exact duplicate scripts were excluded from the implementation.

The new pipeline extracts reusable patterns from these project-owned assets:

- `D:\项目文件202605\制图数据\outputs\figures_clean_v4\scripts\plot_clean_single_indicator_figures_v4.py`
  - Used for: single-indicator cleaning, group summaries, one-way ANOVA, Levene/Tukey-style statistical workflow, bar figures.
- `D:\项目文件202605\制图数据\outputs\oneway_significance_redraw_20260529\scripts\generate_oneway_audit_figures.py`
  - Used for: ANOVA-oriented audit structure, summary tables, significance-aware plotting separation.
- `D:\项目文件202605\科研绘图子项目组\scripts\04_plot_soil_nematode_correlations.py`
  - Used for: Spearman correlation matrix workflow and heatmap-style visualization.
- `D:\项目文件202605\制图数据\scripts\audit_nematode_workbook_20260529.py`
  - Used for: workbook/data cleaning concepts such as text normalization, numeric coercion, sample-id parsing, and audit reporting.
- `D:\项目文件202605\线虫数据表格处理\04_scripts\audit_ppi_special_cases.py`
  - Used for: special-case cleaning and validation patterns.

## Data Boundary

Historical CSV/Excel files were inventoried but not copied or recomputed. This module ships with a small synthetic demo table so the pipeline can be run end-to-end without changing or recalculating the original research outputs.

Candidate historical data files detected during scan include:

- `D:\项目文件202605\制图数据\data\clean\soil_core_variables_latest_long.csv`
- `D:\项目文件202605\制图数据\data\clean\soil_physicochemical_latest_wide.csv`
- `D:\项目文件202605\制图数据\outputs\plant_growth_20260529\plant_growth_plot_long.csv`
- `D:\项目文件202605\制图数据\outputs\nematode_remaining9_20260529\nematode_plot_long_remaining9.csv`
- `D:\项目文件202605\制图数据\outputs\figures_clean_v4\stats\plot_summary_mean_se_clean_v4.csv`

No CSV, Excel workbook, manifest, existing figure, CLD table, or historical statistic was modified during this consolidation.
