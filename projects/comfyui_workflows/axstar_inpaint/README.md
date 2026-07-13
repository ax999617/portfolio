# Inpainting Workflow — Legacy Record

> This graph is retained for provenance and has not completed public-release review. It is not a supported or reproducible portfolio entrypoint.

## Preserved graph

The workflow combines a base image, mask, text prompts, checkpoint/LoRA settings, inpainting encode/decode nodes, sampling, mask blur, compositing, and image saving. `workflow.json` is the historical graph; `example_outputs/` contains a candidate local output whose one-to-one attribution has not been independently confirmed.

## Review requirements

Before reuse, verify model and custom-node versions, input rights, embedded text and image metadata, and exact output attribution. See the parent [publication checklist](../PUBLICATION_CHECKLIST.md).

## Provenance

- Original workflow: `<local-source>/comfyui/workflows/axstar_inpaint.json`
- Candidate output root: `<local-source>/comfyui/output`
- Candidate output: `<local-source>/comfyui/output/axstar_inpaint_composited_00014_.png`
- Source CSV: none identified in this asset set.
