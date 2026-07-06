# Axstar Inpaint Workflow

Source provenance:

- Original workflow file: `E:\ComfyUI-aki-v1.7\ComfyUI\my_workflows\工作流\axstar_inpaint.json`
- Candidate output root: `E:\ComfyUI-aki-v1.7\ComfyUI\output`
- Source CSV: none identified in this asset set

## Problem definition

This workflow packages a inpainting generation pipeline so it can be reviewed, imported, and reproduced in ComfyUI.

## Method

Pipeline logic:

- Input: a base image, a mask/alpha channel, positive and negative text prompts, checkpoint and LoRA settings
- Core nodes: CheckpointLoaderSimple, LoraLoader, LoadImage, LoadImageMask, VAEEncodeForInpaint, KSampler, VAEDecode, ImageCompositeMasked, MaskBlur, SaveImage.
- Output: an inpainted image and a composited image
- Parameter behavior: mask blur changes edge blending; sampler steps/CFG/seed control denoising strength and variation; LoRA strength changes style influence

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

Example output copied from `E:\ComfyUI-aki-v1.7\ComfyUI\output\axstar_inpaint_composited_00014_.png` into `example_outputs/axstar_inpaint_composited_00014_.png`. For generic filename prefixes, treat this as a local output candidate rather than a guaranteed single-workflow artifact.
