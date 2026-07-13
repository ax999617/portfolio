# Data and Artifact Boundaries

This page distinguishes current engineering evidence from historical or machine-local material. It does not assert that every archived asset is reproducible.

## Project boundaries

| Area | Current evidence | Boundary |
|---|---|---|
| Wheat API contract | Synthetic in-memory images, read-only knowledge JSON, 12 service-layer tests | No training images or validated disease model |
| ML pipeline v2 | Configuration, source audit logic, strict checkpoints, 22 synthetic/offline tests | Local source audit record is not a public dataset; no real-data retraining |
| Statistical assets | Four committed CSV snapshots and three frozen reference assets | Visitor gate checks paths only; it does not open values or recompute results |
| ComfyUI archive | Historical workflow JSON and candidate outputs | Publication suitability, dependencies, attribution, and licenses are unresolved |
| Windows automation | Historical AutoHotkey scripts | Runtime syntax mismatch is unresolved |

## Statistical source CSV

Original root: `D:\项目文件202605\制图数据`

- `data\clean\soil_core_variables_latest_long.csv`
- `data\clean\soil_core_variables_latest_v3_long.csv`
- `data\clean\soil_physicochemical_latest_v3_wide.csv`
- `data\clean\soil_physicochemical_latest_wide.csv`

Committed snapshots are under `projects/stats_variance_correlation_pipeline/data/clean/`. The current read-only gate uses `Path.is_file()` only; it does not read their contents.

## Historical artifacts

- Legacy ML weights and the historical training curve are labeled `legacy/unverified`; v2 does not load them.
- CV screenshots demonstrate an earlier UI/API flow, not model quality.
- Statistical PDFs and PNGs are frozen source outputs; no CLD or statistic was regenerated.
- ComfyUI images are candidates whose exact workflow attribution is not guaranteed.

## Provenance labels

- Wheat source: `<local-source>/wheat-disease-demo`
- ML source: `<local-source>/ml-training`; exact machine-local audit paths remain in the collapsed provenance record of the [algorithm report](../projects/ml_training_pipeline/v2/ALGORITHM_REFACTOR_REPORT.md).
- ComfyUI source: `<local-source>/comfyui/workflows`, `<local-source>/comfyui/output`
- Statistical root: `D:\项目文件202605\制图数据`
- No CSV, Excel, manifest, statistic, CLD, model weight, or frozen figure was modified during the visitor-copy review.
