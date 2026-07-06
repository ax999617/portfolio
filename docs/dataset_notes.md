# Dataset Notes

Source provenance:

- Wheat disease demo source: `D:\202604竞赛项目`
- ML training source: `D:\shiwanwuax`
- ComfyUI workflows: `E:\ComfyUI-aki-v1.7\ComfyUI\my_workflows\工作流`
- AutoHotkey runtime: `C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe`
- Source CSV: none identified in the inspected asset sets

## Wheat Disease Demo

The wheat project is represented by backend inference code, knowledge-base JSON, and screenshots from the demo flow. The source backend states that the current inference mode is an MVP demo rule engine with a reserved real-model adapter. Therefore this portfolio does not claim new accuracy results.

Representative screenshots were copied from `D:\202604竞赛项目\screenshots\2026-05-13_backend-demo` into `assets/results/cv_wheat_disease/`.

## ML Training Pipeline

The ML training source contains code, model weights, quantized weights, reference images, history JSON, knowledge JSON, and a training progress figure. The visible class intent is a 3-class image-recognition task for Henan-local categories. The source dataset directory itself was not found as a complete image-folder dataset in the provided root, so the portfolio provides train/eval/inference entrypoint structure without running a new training job.

Copied artifacts:

- Full model weight: `projects/ml_training_pipeline/artifacts/weights/trained.pth`
- Quantized weights: `projects/ml_training_pipeline/artifacts/weights/quantized.pth`, `projects/ml_training_pipeline/artifacts/weights/quantized_model.pth`
- Training progress image: `assets/results/ml_training_pipeline/training_progress.png`

## ComfyUI Workflows

Four workflow JSON files were copied from the workflow root. Example images were copied only when local output filenames could be treated as reasonable candidates. Workflow READMEs distinguish exact copied workflow JSON from candidate output images.

## Automation Scripts

The user-provided AutoHotkey path is a runtime executable, not a script. Custom scripts were located under `D:\shiwanwuax\haiku4.5\AutoHotkey` and copied into the low-priority system tools project.

## Constraints Followed

Existing source files were not edited. No CSV, Excel, or manifest files were modified. No statistical metrics, CLD letters, or frozen figures were recomputed or redrawn.
