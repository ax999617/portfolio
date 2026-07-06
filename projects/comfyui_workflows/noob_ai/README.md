# Noob AI Text-To-Image Workflow

Source provenance:

- Original workflow file: `<local-source>/comfyui/workflows/noob ai工作流.json`
- Candidate output root: `<local-source>/comfyui/output`
- Source CSV: none identified in this asset set

## Problem definition

This workflow packages a LoRA-assisted text-to-image generation pipeline so it can be reviewed, imported, and reproduced in ComfyUI.

## Method

Pipeline logic:

- Input: positive and negative prompts, checkpoint, LoRA stack, latent size, seed, sampler, steps, and CFG
- Core nodes: CheckpointLoaderSimple, multiple LoraLoader nodes, CLIPTextEncode, EmptyLatentImage, KSampler, VAEDecodeTiled, SaveImage.
- Output: a saved generated image
- Parameter behavior: LoRA strengths steer style; latent dimensions set composition size; sampler steps and CFG trade detail against prompt adherence

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

Example output copied from `<local-source>/comfyui/output/NoobAI_character_pose_00011_.png` into `example_outputs/NoobAI_character_pose_00011_.png`. For generic filename prefixes, treat this as a local output candidate rather than a guaranteed single-workflow artifact.
