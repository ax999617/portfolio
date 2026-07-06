# ML Training Pipeline

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

The model family is based on a ResNet-18 classifier with a 3-class output head. The extracted preprocessing contract uses 224x224 resizing and ImageNet normalization. Existing artifacts include a full trained weight file and two quantized weight files.

The portfolio version separates the workflow into:

- `src/train/train.py` for training entrypoint structure.
- `src/eval/evaluate.py` for evaluation entrypoint structure.
- `src/inference/predict.py` for single-image inference.
- `src/models/` for model definitions and quantization code.
- `configs/` for extracted model and preprocessing configuration.

## Implementation

Original scripts were not left as a flat dump. They were placed under ownership-oriented modules:

- `src/data/dataset_processing.py` from the source dataset loader.
- `src/models/trained.py` from the source trained model definition.
- `src/models/quantized.py` from the source quantization pipeline.
- `src/app/gui_legacy.py` from the source Tkinter GUI.
- `src/orchestration/main_legacy.py` from the original launcher.
- `artifacts/weights/` contains copied `.pth` model artifacts.
- `artifacts/metadata/` contains copied history and knowledge JSON.

## How to run

Install the ML dependencies in a Python environment with PyTorch:

```bash
cd projects/ml_training_pipeline
pip install -r requirements.txt
```

Single-image inference:

```bash
python src/inference/predict.py --image ../../assets/images/ml_training_pipeline/luoyang_peony_ref.jpg --weights artifacts/weights/trained.pth
```

Training and evaluation entrypoints are prepared but not executed during consolidation:

```bash
python src/train/train.py --data-dir path/to/imagefolder_dataset --output artifacts/weights/retrained.pth
python src/eval/evaluate.py --data-dir path/to/imagefolder_dataset --weights artifacts/weights/trained.pth
```

## Results

The original training progress image is stored in `../../assets/results/ml_training_pipeline/training_progress.png`. Existing trained and quantized weights were copied into `artifacts/weights/` for reproducible local inference. No new training run or metric recomputation was performed.
