# Training Handoff — Legacy Note

> This handoff describes an early adapter idea, not a validated training or integration path. The real wheat training loop was not present in the inspected source. Use the current [API contract service](../../../cv_wheat_disease_test_v1/README.md) for tested service behavior.

Source provenance:

- Original wheat demo source: `<local-source>/wheat-disease-demo`
- Real wheat training loop: not present in the inspected source directory
- Source CSV: none identified in this asset set

The legacy CV demo attempted to separate inference from training through `src/inference/model_inference.py`; the adapter is incomplete and is not treated as stable evidence.

Any future classifier integration must independently validate the class order, preprocessing, checkpoint contract, evaluation set, and failure behavior. It should be injected into the current service boundary and must fail closed when unavailable; the legacy `INFERENCE_MODE=model` path is not the recommended implementation.
