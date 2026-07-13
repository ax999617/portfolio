# ML Training Pipeline

> **Status:** This directory is a preserved legacy prototype. Its historical weights and
> quantized artifacts have incompatible model/class contracts and are not treated as a
> validated reproducible baseline. The active, fail-closed refactor is documented in
> [`v2/README.md`](v2/README.md); legacy code and artifacts remain unchanged for provenance.

Source provenance:

- Original project root: `<local-source>/ml-training`
- Training/model files: `<local-source>/ml-training`
- Model artifacts: `<local-source>/ml-training/model`
- Reference images: `<local-source>/ml-training/reference_images`
- Source CSV: none identified in this asset set

## Problem definition

This project restructures the original image-recognition code into a standard machine-learning project layout. The source assets describe a 3-class classifier for Henan-local visual categories: Luoyang peony, Zhengzhou Shang-dynasty bronze artifact, and Xinyang Maojian tea plant.

This is separate from the wheat disease demo. It is kept as the core ML engineering project because it contains model definitions, preprocessing code, trained weights, quantized weights, GUI inference logic, and experiment metadata.

## Method

The model family is based on a ResNet-18 classifier with a 3-class output head. The extracted preprocessing contract uses 224x224 resizing and ImageNet normalization. Existing artifacts include one historical state-dict artifact and two historical quantized state-dict artifacts.

The portfolio version separates the workflow into:

- `src/train/train.py` for training entrypoint structure.
- `src/eval/evaluate.py` for evaluation entrypoint structure.
- `src/inference/predict.py` for single-image inference.
- `src/models/` for model definitions and quantization code.
- `configs/` for extracted model and preprocessing configuration.

## Active v2 refactor

`v2/` provides a separate MobileNetV3-Small transfer-learning pipeline with an explicit
class order, strict checkpoints, frozen-backbone training, CUDA AMP, early stopping,
best/last checkpoints, exact-duplicate leakage checks, and offline synthetic tests. It
does not load or reinterpret the legacy weights. The current portfolio emphasis is the
algorithm and reliability design; see `v2/ALGORITHM_REFACTOR_REPORT.md`. Historical model
results remain labeled as legacy evidence while real v2 training is deferred.

## Implementation

Original scripts were not left as a flat dump. They were placed under ownership-oriented modules:

- `src/data/dataset_processing.py` from the source dataset loader.
- `src/models/trained.py` from the source trained model definition.
- `src/models/quantized.py` from the source quantization pipeline.
- `src/app/gui_legacy.py` from the source Tkinter GUI.
- `src/orchestration/main_legacy.py` from the original launcher.
- `artifacts/weights/` contains copied `.pth` model artifacts.
- `artifacts/metadata/` contains copied history and knowledge JSON.

## Execution status

Do not use the archived inference, training, or evaluation commands as a validated workflow. In particular, loading `artifacts/weights/trained.pth` through the current legacy model definition leaves an incompatible classification head and cannot produce trustworthy predictions.

Use the active [`v2/README.md`](v2/README.md) entrypoints for dataset audit, synthetic verification, and any future experiment. The legacy scripts remain readable only to preserve the early implementation history.

## Results

The original training progress image is stored in `../../assets/results/ml_training_pipeline/training_progress.png`. Existing trained and quantized weights remain in `artifacts/weights/` as unverified historical artifacts; they are not used by v2 and are not presented as reproducible inference evidence. No new training run or metric recomputation was performed during the v2 code refactor.
