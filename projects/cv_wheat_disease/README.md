# Wheat Disease Demo — Legacy Prototype

> **Archive status:** this early demo does not contain a completed real-model adapter and is not the recommended runtime. Review the current [Wheat Disease API Contract](../cv_wheat_disease_test_v1/README.md) for the validated service boundary and tests.

## What is preserved

The directory records an early FastAPI-oriented product flow: image upload, a demo class result, risk messaging, knowledge fields, and report-oriented output. It is useful as implementation history, not as evidence of a trained disease-recognition model.

- `src/inference/` contains the legacy inference surface and demo fallback.
- `src/services/` contains risk and response assembly.
- `src/knowledge/wheat_diseases.json` contains the preserved knowledge content.
- `src/main.py` preserves the earlier API application.
- `src/training/README.md` documents the missing training handoff rather than fabricating it.
- `assets/results/cv_wheat_disease/` contains historical UI/API screenshots.

## Known limitations

- the real predictor hook is incomplete;
- demo classification behavior must not be interpreted as model accuracy;
- the legacy application is not covered by the current service-layer tests;
- legacy import/output, CORS, and upload-handling behavior has not been accepted as a production boundary.

For these reasons, the previous run instructions are intentionally not presented as the default portfolio path.

## Provenance

- Original project root: `<local-source>/wheat-disease-demo`
- Backend source: `<local-source>/wheat-disease-demo/后端`
- Result screenshots: `<local-source>/wheat-disease-demo/screenshots/2026-05-13_backend-demo`
- Source CSV: none identified in this asset set.
- No new accuracy, statistic, CLD, weight, or frozen screenshot was produced or modified.
