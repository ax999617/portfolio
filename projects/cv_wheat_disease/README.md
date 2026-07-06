# CV Wheat Disease Recognition Demo

Source provenance:

- Original project root: `<local-source>/wheat-disease-demo`
- Backend source: `<local-source>/wheat-disease-demo/后端`
- Result screenshots: `<local-source>/wheat-disease-demo/screenshots/2026-05-13_backend-demo`
- Source CSV: none identified in this asset set

## Problem definition

This project presents a computer-vision classification workflow for wheat disease recognition. The portfolio version focuses on the end-to-end inference surface: image upload, disease class prediction, confidence, risk warning, knowledge explanation, and report-oriented output.

The original backend explicitly marks the current mode as a demo MVP. The real model hook is separated from the demo rule engine so a trained EfficientNet, MobileNet, or other classifier can be connected without changing the API response contract.

## Method

The workflow is organized as:

1. Image bytes enter a unified inference function.
2. `INFERENCE_MODE=model` tries the real model adapter.
3. If model inference is unavailable, the code falls back to a deterministic demo rule engine.
4. The class result is passed to a risk engine.
5. A response builder joins prediction, risk, knowledge base fields, and a disclaimer into one JSON response.

Disease classes represented by the demo interface include healthy wheat, stripe rust, leaf rust, powdery mildew, and fusarium.

## Implementation

- `src/inference/` contains the separated inference interface and demo fallback.
- `src/services/` contains risk scoring and response assembly.
- `src/knowledge/wheat_diseases.json` contains disease explanation content copied from the original backend.
- `src/main.py` preserves the FastAPI application surface from the original backend.
- `src/training/README.md` documents the training handoff contract. The wheat training loop was not present in this source directory, so it is intentionally not fabricated.
- `configs/inference_config.json` records the portfolio inference mode and class contract.

## How to run

Run the lightweight inference demo:

```bash
cd projects/cv_wheat_disease
python scripts/run_inference_demo.py --image ../../assets/results/cv_wheat_disease/02_frontend_upload_result_1.png
```

Run the preserved FastAPI backend surface:

```bash
cd projects/cv_wheat_disease/src
pip install -r ../requirements.txt
python main.py
```

Then open `http://127.0.0.1:8000/docs`.

## Results

Representative outputs are stored in `../../assets/results/cv_wheat_disease/`. They include the frontend upload flow, Swagger API documentation, API response example, bilingual API guide, and PDF report buttons from the original demo screenshots.

No new accuracy, CLD, or statistical metric was recomputed during this portfolio consolidation.
