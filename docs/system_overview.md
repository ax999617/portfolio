# System Overview

Source provenance:

- Current portfolio root: `D:\工作流\portfolio`
- Original wheat demo: `D:\202604竞赛项目`
- Original ML training code: `D:\shiwanwuax`
- Original ComfyUI workflows: `E:\ComfyUI-aki-v1.7\ComfyUI\my_workflows\工作流`
- AutoHotkey runtime and scripts: `C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe`, `D:\shiwanwuax\haiku4.5\AutoHotkey`
- Source CSV: none identified in the inspected asset sets

## Repository Map

```text
portfolio/
  README.md
  projects/
    cv_wheat_disease/       # CV inference demo and backend surface
    ml_training_pipeline/   # train/eval/inference ML structure
    comfyui_workflows/      # documented ComfyUI workflow packages
    system_tools/           # low-priority AutoHotkey utility
    misc_tools/             # support notes
  assets/
    images/                 # reference and sample images
    results/                # copied result screenshots/figures
    diagrams/               # architecture map
  docs/
    dataset_notes.md
    methodology.md
    system_overview.md
```

## High-Level Flow

```mermaid
flowchart LR
  A["Local scattered assets"] --> B["Read-only inspection"]
  B --> C["Project taxonomy"]
  C --> D["Standard project directories"]
  D --> E["README + configs + run entrypoints"]
  E --> F["Recruiter-readable portfolio"]
```

## Risk Notes

- The wheat disease backend is a demo MVP unless a real model is connected through the existing adapter.
- The ML project includes weights and inference structure, but no new training metrics were generated.
- ComfyUI output images are copied conservatively and labeled according to traceability.
- AutoHotkey scripts are documented as a utility appendix and may require a v1-compatible runtime.
