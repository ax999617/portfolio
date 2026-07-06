# Methodology

Source provenance:

- Source roots: `<local-source>/wheat-disease-demo`, `<local-source>/ml-training`, `<local-source>/comfyui/workflows`, `AutoHotkey v2 runtime`
- Source CSV: none identified in the inspected asset sets

## Consolidation Approach

The portfolio was organized around project intent rather than original disk layout:

- Application demo assets became `cv_wheat_disease`.
- Model code, weights, preprocessing, quantization, and GUI logic became `ml_training_pipeline`.
- Workflow JSON files became documented ComfyUI subprojects.
- AutoHotkey scripts became a low-priority utility project.

## Engineering Refactor

The refactor avoided a flat copy by adding:

- README files with problem, method, implementation, run instructions, and results.
- Config files that extract model classes, image preprocessing, and artifact paths.
- Separate train, eval, and inference entrypoints for the ML project.
- A lightweight CV inference demo script that exercises the backend inference/risk/response chain.
- Per-workflow ComfyUI explanations covering input, nodes, output, and parameters.

## Reproducibility Boundary

The portfolio is reproducible at the project-structure and local-inference level. It does not fabricate missing training results, does not rerun training, and does not infer metrics absent from the source assets.
