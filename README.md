# Portfolio

This is Axing's (阿星) public portfolio repository for internship presentation. It organizes selected local engineering, data analysis, machine learning, and generative-workflow projects into readable, reproducible modules with representative outputs.

The focus is not a raw file dump: each module has a clear project story, scoped source assets, reproducible entrypoints, and results that can be reviewed directly from the repository.

## Capability Areas

**Computer Vision / ML**

- `projects/cv_wheat_disease/`: Wheat disease visual-classification demo with separated inference logic, risk explanation, and sample UI/backend outputs.
- `projects/ml_training_pipeline/`: Refactored image-recognition training pipeline with config files, model artifacts, train/eval/inference separation, and reference assets.

**Data Analysis**

- `projects/stats_variance_correlation_pipeline/`: Statistical analysis pipeline for data cleaning, variance analysis, correlation matrices, figure generation, and PDF report export.
- `docs/dataset_notes.md`: Short notes on dataset boundaries and reproducibility assumptions.

**Generative Pipeline (ComfyUI)**

- `projects/comfyui_workflows/`: Documented ComfyUI workflows split by use case, with sanitized workflow files and example outputs.

**System Tools / Automation**

- `projects/system_tools/`: Small AutoHotkey utility module for desktop automation.
- `projects/misc_tools/`: Supporting notes for repository organization.

## Recommended Reading Order

1. `projects/cv_wheat_disease/README.md`
2. `projects/ml_training_pipeline/README.md`
3. `projects/stats_variance_correlation_pipeline/README.md`
4. `projects/comfyui_workflows/README.md`
5. `docs/methodology.md`

## Repository Structure

```text
portfolio/
|-- projects/
|   |-- cv_wheat_disease/
|   |-- ml_training_pipeline/
|   |-- stats_variance_correlation_pipeline/
|   |-- comfyui_workflows/
|   |-- system_tools/
|   `-- misc_tools/
|-- assets/
|   |-- images/
|   |-- results/
|   `-- diagrams/
`-- docs/
```

## Reproducibility

Each project includes its own README with the problem definition, method, implementation layout, run instructions, and output examples. Local absolute paths and private machine details are intentionally omitted from this cloud version.
