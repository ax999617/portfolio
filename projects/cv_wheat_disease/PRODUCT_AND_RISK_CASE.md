# Wheat Image Analysis API — Product Risk Case

## Scope

This case study defines the product and safety boundary around an image-analysis API: upload, validated input, a structured class result, risk messaging, knowledge fields, and a review recommendation. The current implementation uses an explicit mock by default, so the evidence is limited to API behavior and risk communication rather than diagnostic accuracy.

## Intended users

- API integrators who need stable request, response, and error contracts;
- maintainers who need visible provider failures and fail-closed behavior;
- domain reviewers who must distinguish software output from professional or laboratory review.

## Acceptance criteria

1. The same input produces a stable mock response labeled `demo_mock`.
2. Empty, oversized, over-dimensioned, corrupt, or format-mismatched files are rejected before prediction.
3. No configured provider uses the explicit demo mode; an injected provider failure returns a provider error and no mock result.
4. Unknown classes and out-of-range confidence values fail closed.
5. Model and mock risk messages are not conflated.
6. Importing the service does not create repository outputs.

## Request flow

```text
select image
  -> bounded decode and format validation
  -> injected predictor or explicit demo mock
  -> prediction contract validation
  -> risk and knowledge assembly
  -> JSON response with disclaimer
```

## Failure behavior

| Condition | Response |
|---|---|
| Empty or corrupt file | Reject with a structured validation error |
| File or decoded pixels exceed limits | Stop before prediction |
| MIME, extension, and decoded format disagree | Reject the request |
| Injected provider is unavailable or fails | Return a provider error and fail closed; do not substitute a mock result |
| Provider result violates the contract | Fail closed; do not return a fabricated success |

## Evidence

- Current implementation: [`../cv_wheat_disease_test_v1/`](../cv_wheat_disease_test_v1/README.md)
- Read-only knowledge source: `src/knowledge/wheat_diseases.json`
- Historical UI/API screenshots: `../../assets/results/cv_wheat_disease/`

## Next engineering steps

- inject a separately validated model whose classes and preprocessing match the response contract;
- add HTTP route and multipart tests;
- add a reviewed evaluation set and human escalation workflow;
- add deployment, logging, latency, and error-rate monitoring before production use.

## Provenance and source CSV / 溯源与来源 CSV

- Repository: `D:\工作流\portfolio`
- Original project label: `<local-source>/wheat-disease-demo`
- Source CSV / 来源 CSV: none identified; this module does not depend on CSV.
- No model was trained and no weight, metric, CSV, Excel, manifest, CLD, or frozen screenshot was changed.
