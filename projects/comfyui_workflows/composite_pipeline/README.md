# Composite Control Pipeline

Source provenance:

- Original workflow file: `E:\ComfyUI-aki-v1.7\ComfyUI\my_workflows\工作流\综合工作流.json`
- Candidate output root: `E:\ComfyUI-aki-v1.7\ComfyUI\output`
- Source CSV: none identified in this asset set

## Problem definition

This workflow packages a multi-stage ControlNet and regional-detail generation pipeline so it can be reviewed, imported, and reproduced in ComfyUI.

## Method

Pipeline logic:

- Input: source image/control signals, detector settings, prompts, checkpoint, LoRAs, masks, tile settings, and sampler settings
- Core nodes: ControlNetApplyAdvanced, UltralyticsDetectorProvider, VAEEncode/VAEDecode, KSampler, tiling/batch nodes, image comparison, previews, and metadata saving.
- Output: intermediate previews and saved detailed/upscaled images with metadata
- Parameter behavior: ControlNet weights affect structure preservation; detector thresholds affect selected regions; tile/upscale settings affect detail and memory use

## Implementation

- `workflow.json` is copied from the original local workflow.
- `example_outputs/` stores representative local outputs when available.
- The README explains the graph at pipeline level so the JSON is not an opaque dump.

## How to run

1. Start ComfyUI from the local installation.
2. Import this directory's `workflow.json`.
3. Confirm referenced checkpoint, LoRA, ControlNet, and custom-node dependencies are installed.
4. Set input image or prompt values.
5. Queue the workflow and inspect saved images.

## Results

Example output copied from `E:\ComfyUI-aki-v1.7\ComfyUI\output\ComfyUI_02152_.png` into `example_outputs/ComfyUI_02152_.png`. For generic filename prefixes, treat this as a local output candidate rather than a guaranteed single-workflow artifact.
