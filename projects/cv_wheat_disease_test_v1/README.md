# Wheat Disease API Contract Service

## Purpose

This project isolates a service-layer contract from the legacy wheat demo. It demonstrates bounded image handling, a replaceable predictor interface, an explicit deterministic mock, risk and knowledge response assembly, and failure-path testing. It does **not** perform wheat-disease recognition.

## Request path

```text
uploaded bytes
  -> file-size and pixel limits
  -> full image decode
  -> MIME / extension / decoded-format consistency
  -> injected predictor (optional)
  -> explicit deterministic mock mode when no provider is configured
  -> prediction contract validation
  -> risk + knowledge + disclaimer response
```

Verified behavior:

- imports do not create files or directories;
- uploads are capped at 5 MiB and 20 million decoded pixels;
- PNG, JPEG, WebP, BMP, and TIFF inputs must decode successfully;
- the filename extension and supplied MIME type must match the decoded image format;
- mock results are stable for identical bytes and filenames and are labeled `demo_mock`;
- default demo mode states that no real model is configured;
- once a real provider is injected, provider errors fail closed instead of returning mock classifications;
- invalid provider classes or confidence values fail closed;
- model and mock risk messages remain semantically distinct.

## Tests

From the repository root:

```powershell
python -m unittest discover -s projects/cv_wheat_disease_test_v1/tests -p "test*_test_v1.py" -v
```

The 12 service-layer tests use synthetic in-memory images and the repository's read-only knowledge JSON. They do not read training images, train a model, or write repository outputs. The FastAPI adapter exists, but HTTP status, multipart, and route behavior are not yet covered by automated tests.

## Optional FastAPI adapter

```powershell
Set-Location projects/cv_wheat_disease_test_v1
python -m pip install -r requirements_test_v1.txt
$env:PYTHONPATH = ".\src"
python -m uvicorn wheat_demo_test_v1.api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs`. The default application instance is demo-only until a separately validated predictor is injected.

## Project map

```text
cv_wheat_disease_test_v1/
|-- README.md
|-- requirements_test_v1.txt
|-- src/wheat_demo_test_v1/
|   |-- api.py
|   `-- service.py
`-- tests/test_service_contract_test_v1.py
```

## Provenance and source CSV / 溯源与来源 CSV

- Repository: `D:\工作流\portfolio`
- Legacy module: `D:\工作流\portfolio\projects\cv_wheat_disease`
- Original source label: `<local-source>/wheat-disease-demo`
- Knowledge source: `projects/cv_wheat_disease/src/knowledge/wheat_diseases.json`
- Source CSV / 来源 CSV: none identified; this module does not depend on CSV.
- No model weight, screenshot, CSV, Excel, manifest, statistic, CLD, or frozen figure was modified.
