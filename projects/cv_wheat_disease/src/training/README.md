# Training Handoff

Source provenance:

- Original wheat demo source: `<local-source>/wheat-disease-demo`
- Real wheat training loop: not present in the inspected source directory
- Source CSV: none identified in this asset set

The CV wheat demo separates inference from training by keeping a stable model adapter in `src/inference/model_inference.py`.

To connect a real classifier, train a model outside this demo, export a `.pth` file, implement `_try_real_model_inference`, and set `INFERENCE_MODE=model`. The API response shape should remain unchanged so the frontend and reporting path do not need to change.
