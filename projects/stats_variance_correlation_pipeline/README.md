# Stats Variance Correlation Pipeline

This module is a source-derived statistical analysis capability extracted from the historical research plotting corpus under:

- `D:\项目文件202605\制图数据`
- approved scientific result source: `D:\项目文件202605\制图数据\科研用图_B2v2v3`
- SPSS result source: `D:\项目文件202605\制图数据\SPSS原数据图片`

It is not a dump of historical scripts. The scattered assets were filtered, normalized into a single project structure, and represented as a reproducible pipeline for clean-data provenance, result packaging, figure preview generation, and optional variance/correlation analysis on new input data.

## Analysis Goal

The source corpus supports experiment-style statistical reporting: soil nitrogen indicators, soil physicochemical variables, plant-growth indicators, nematode indices, and PPI-style metrics were cleaned, summarized, tested by variance-analysis workflows, plotted, and exported as publication-ready PDF figures.

This portfolio module shows that workflow as an independent data-analysis and statistical-modeling pipeline:

- preserve frozen historical result figures without recalculating statistics or CLD letters;
- extract effective code assets for data cleaning, ANOVA/Tukey/CLD-aware plotting, statistical visualization, and PDF export;
- expose a reusable tabular analysis path for future datasets requiring group summaries, variance components, and correlation matrices;
- regenerate all portfolio preview images and the package report from committed source assets.

## Method

Historical scripts were scanned for five themes: variance analysis, correlation/correlation matrix, data cleaning, statistical plotting, and PDF report/export. Third-party package examples, temporary files, test scripts, exact duplicates, and copy/template fragments were excluded.

The default pipeline does not recompute historical ANOVA, post-hoc tests, CLD labels, or source CSV/Excel files. Instead it:

1. loads the curated source-asset catalog;
2. preserves exact copies of clean source CSV files under `data/clean/`;
3. reads the selected frozen result assets from `reference_results/original/` or the local source root;
4. renders the two selected scientific PDFs into PNG previews under `outputs/result_assets/previews/`;
5. copies the selected SPSS image into the preview set under `outputs/result_assets/previews/`;
6. writes `outputs/asset_package_summary.json`;
7. exports `outputs/report.pdf` with provenance, method boundaries, and result previews.

The optional `--analysis-input` path uses the reusable functions in `src/table_methods.py` for new data only. It standardizes a long table, computes group summaries and variance components, and creates a correlation matrix. It does not run Tukey/CLD logic and is not used for the frozen source results.

## Project Structure

```text
stats_variance_correlation_pipeline/
|-- data/
|   |-- clean/                        # exact copies from D:\项目文件202605\制图数据\data\clean
|   `-- source_asset_catalog.json     # generated source catalog with provenance
|-- reference_results/original/       # committed frozen result assets used for reproducible runs
|-- outputs/
|   |-- result_assets/previews/       # regenerated PNG previews
|   |-- asset_package_summary.json
|   `-- report.pdf
|-- src/
|   |-- assets.py                     # asset copy/render pipeline
|   |-- catalog.py                    # curated source/result asset definitions
|   |-- report.py                     # PDF report export
|   |-- table_methods.py              # optional cleaning, variance, and correlation methods
|   `-- visualization.py              # optional statistical figure helpers
|-- run_pipeline.py
|-- source_asset_inventory.md
`-- requirements.txt
```

## How To Run

From this directory:

```bash
pip install -r requirements.txt
python run_pipeline.py
```

Use the original local source root when available:

```bash
python run_pipeline.py --source-root "D:\项目文件202605\制图数据"
```

Run the optional reusable analysis path on the copied clean source data:

```bash
python run_pipeline.py --analysis-input data/clean/soil_physicochemical_latest_v3_wide.csv --group-col N --sample-col SampleID
```

Run the optional reusable analysis path on another new CSV:

```bash
python run_pipeline.py --analysis-input path/to/new_table.csv --group-col treatment --sample-col sample_id
```

The optional input can be long format with `sample_id`, `group`, `metric`, `value`, or wide format with one grouping column and numeric measurement columns.

## Output Examples

Selected frozen result assets:

- `reference_results/original/Fig_NH4N_methodB2v2_01.pdf`
- `reference_results/original/Fig_NO3N_methodB2v2_01.pdf`
- `reference_results/original/SPSS_NO3-N.png`

Regenerated previews:

![NH4-N scientific PDF preview](outputs/result_assets/previews/Fig_NH4N_methodB2v2_01.png)

![NO3-N scientific PDF preview](outputs/result_assets/previews/Fig_NO3N_methodB2v2_01.png)

![SPSS NO3-N source image](outputs/result_assets/previews/SPSS_NO3-N.png)

PDF report:

- `outputs/report.pdf`

All previews and the report can be regenerated by `python run_pipeline.py` from the committed reference assets.

## Reproducibility Boundary

- Clean source CSV files from `D:\项目文件202605\制图数据\data\clean` are copied exactly into `data/clean/`.
- No historical Excel workbook, manifest, CLD table, or frozen figure is modified.
- The two scientific PDFs are preserved as original result assets and rendered only for README/report previews.
- The SPSS result image is stored once as a reference original and copied only as a preview asset under `outputs/`.
- Source provenance is retained in `source_asset_inventory.md`, `data/source_asset_catalog.json`, and `outputs/asset_package_summary.json`.
