# ComfyUI Workflows

Source provenance:

- Workflow root: `<local-source>/comfyui/workflows`
- Candidate output image root: `<local-source>/comfyui/output`
- Source CSV: none identified in this asset set

## Problem definition

This project packages local ComfyUI workflows so they can be reviewed as reproducible generative pipelines rather than unexplained JSON files.

## Method

Each workflow is split into its own subdirectory with the original `workflow.json`, a README that explains inputs, node logic, outputs, and parameter effects, plus example outputs when a reliable local output candidate exists.

## Implementation

- `axstar_inpaint/` packages an inpainting workflow.
- `noob_ai/` packages a LoRA-based text-to-image character workflow.
- `regional_anime/` packages a regional/two-dimensional style workflow.
- `composite_pipeline/` packages a large multi-stage ControlNet and regional-detail workflow.

## How to run

Open ComfyUI, import a subdirectory's `workflow.json`, confirm model/checkpoint/LoRA paths exist in the local ComfyUI installation, set prompts or input images, then queue the graph.

Cloud note: workflow files have been sanitized for publication. Model references are relative placeholders such as `models/...`; replace them with the model names or subpaths available in your local ComfyUI setup before running.

## Results

Example outputs are included only when they can be traced to local ComfyUI output naming conventions. Ambiguous global outputs are labeled as candidates, not definitive workflow results.
