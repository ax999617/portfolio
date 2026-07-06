# Stats Variance Correlation Pipeline

Source provenance:

- Scanned root: `<local-source>/historical-statistics`
- Primary source project root: `<local-source>/stats-project`
- Key historical scripts: see `source_asset_inventory.md`
- Source CSV copied into this module: none
- Reproducible demo CSV: `data/example_measurements.csv`

## Problem definition

This project is a data analysis and statistical modeling pipeline for tabular experiment data. It answers two common questions:

- Do treatment groups differ in measured indicators? This is handled through group summaries and one-way variance analysis.
- How do numeric indicators move together across samples? This is handled through a reproducible correlation matrix and heatmap.

The module was created from historical local assets related to variance analysis, correlation analysis, statistical plotting, data cleaning, and PDF export. It is an independent portfolio capability module, not a folder of copied scripts.

## Method

The pipeline uses a long-format table with `sample_id`, `group`, `metric`, and `value`.

- Data cleaning standardizes column names, coerces numeric values, drops missing rows, removes duplicate sample/group/metric records, and writes a cleaning audit.
- Variance analysis computes group-level `n`, mean, standard deviation, standard error, variance, and one-way ANOVA statistics per metric.
- Correlation logic pivots the cleaned table to sample-by-metric format and computes a Pearson, Spearman, or Kendall correlation matrix.
- Plotting generates reproducible figures from the computed outputs: group mean +/- SE, ANOVA effect sizes, and correlation heatmap.
- PDF export writes a multi-page `outputs/report.pdf` using matplotlib `PdfPages`.

No historical CSV/Excel file, manifest, CLD table, or frozen figure is modified or recomputed by this project. The included demo outputs are generated from the new synthetic example CSV only.

## Implementation

```text
stats_variance_correlation_pipeline/
  src/
    data_processing.py   # loading, long/wide normalization, cleaning audit
    analysis.py          # group summaries, one-way ANOVA, correlation matrix
    plotting.py          # regenerated PNG figures
    pdf_report.py        # PDF report export
  data/
    example_measurements.csv
  outputs/
    figures/
    report.pdf
  run_pipeline.py
  source_asset_inventory.md
```

## How to run

From this directory:

```bash
pip install -r requirements.txt
python run_pipeline.py
```

Use your own CSV or Excel file:

```bash
python run_pipeline.py --input path/to/table.csv --group-col treatment --metric-col indicator --value-col value --sample-col sample_id
```

Choose a correlation method:

```bash
python run_pipeline.py --correlation-method pearson
```

## Results

Running the pipeline writes all outputs under `outputs/`:

- `outputs/cleaned_data.csv`
- `outputs/cleaning_report.csv`
- `outputs/group_summary.csv`
- `outputs/anova_results.csv`
- `outputs/correlation_matrix.csv`
- `outputs/figures/group_mean_se.png`
- `outputs/figures/anova_effect_sizes.png`
- `outputs/figures/correlation_heatmap.png`
- `outputs/report.pdf`

These figures and the PDF are regenerated from the input table each time the pipeline is run.
