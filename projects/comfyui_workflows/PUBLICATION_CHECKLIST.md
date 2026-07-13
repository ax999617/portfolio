# Generative Workflow Release Checklist

## Current status

The existing ComfyUI directory is a mixed historical archive. It has not completed content, metadata, dependency, attribution, and license review, so it is excluded from the recommended portfolio path. This checklist records the conditions for a future, independently rebuilt case study; it does not certify the archived files.

## Release checklist

1. **Defined task:** document the user goal, inputs, expected output, and unacceptable output.
2. **Locked dependencies:** record the ComfyUI version, custom-node repositories and commits, model/LoRA identifiers, and reuse terms.
3. **Content review:** inspect prompt text, node titles, notes, model references, and visible output content against the intended audience.
4. **Metadata review:** remove unnecessary prompt, workflow, local path, and personal metadata from exported images, then inspect again.
5. **Attribution:** record seed, source inputs, and the exact workflow/output relationship; label uncertain images as candidates rather than results.
6. **Failure analysis:** document missing models, incompatible nodes, composition drift, mask boundaries, and memory constraints.
7. **License decision:** withhold any model, input, workflow, or output whose publication and reuse terms cannot be explained.

## Recommended future case structure

```text
safe_case_v2/
|-- README.md
|-- workflow.json
|-- dependencies.md
|-- inputs/README.md
`-- outputs/README.md
```

The case README should explain the task, node choices, parameter effects, verification method, failure handling, and unproven claims. A new case should be built from reviewed sources rather than copied from the mixed archive.

## Provenance and source CSV / 溯源与来源 CSV

- Repository directory: `D:\工作流\portfolio\projects\comfyui_workflows`
- Original source labels: `<local-source>/comfyui/workflows`, `<local-source>/comfyui/output`
- Source CSV / 来源 CSV: none identified; this archive does not depend on CSV.
- No workflow, image, metadata, dependency, CSV, Excel, manifest, statistic, CLD, or frozen figure was changed by this checklist.
