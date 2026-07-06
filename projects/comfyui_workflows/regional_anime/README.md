# Regional Anime Workflow

Source provenance:

- Original workflow file: `E:\ComfyUI-aki-v1.7\ComfyUI\my_workflows\工作流\分区工作流（二次元）.json`
- Candidate output root: `E:\ComfyUI-aki-v1.7\ComfyUI\output`
- Source CSV: none identified in this asset set

## Problem definition

This workflow packages a regional style generation generation pipeline so it can be reviewed, imported, and reproduced in ComfyUI.

## Method

Pipeline logic:

- Input: prompt text, LoRA settings, latent canvas, sampler settings, and seed
- Core nodes: CheckpointLoaderSimple, LoraLoader, CLIPTextEncode, EmptyLatentImage, KSampler, VAEDecode, SaveImage.
- Output: a saved stylized image
- Parameter behavior: prompt regions and LoRA strength influence local style; seed controls variation; sampler settings control texture/detail

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

Example output copied from `E:\ComfyUI-aki-v1.7\ComfyUI\output\Illustrious_character_pose_00004_.png` into `example_outputs/Illustrious_character_pose_00004_.png`. For generic filename prefixes, treat this as a local output candidate rather than a guaranteed single-workflow artifact.
