# Wheat Disease API Contract Demo - test v1

## Purpose

This versioned refactor isolates the recruiter-facing API contract from the legacy patent/model stubs. It demonstrates input validation, a replaceable predictor interface, deterministic mock fallback, risk/knowledge response assembly, and failure-path tests. It does **not** perform wheat-disease recognition.

## Design

```text
uploaded bytes
  -> bounded input validation
  -> injected real predictor (optional)
  -> explicit deterministic mock fallback
  -> prediction contract validation
  -> risk + knowledge + disclaimer response
```

Key properties:

- importing the package does not create files or directories;
- the mock result is stable for the same bytes and filename and is labeled `demo_mock`;
- missing or failed real providers expose a fallback reason;
- invalid provider classes or confidence values fail closed;
- image size, type, extension, and byte signature are checked before prediction;
- the existing knowledge JSON is read without modification.

## Run tests

From the repository root:

```powershell
python -m unittest discover -s projects/cv_wheat_disease_test_v1/tests -p "test*_test_v1.py" -v
```

The tests use in-memory bytes and temporary objects only. They do not read real wheat images, train a model, or write repository outputs.

## Run the optional FastAPI adapter

```powershell
Set-Location projects/cv_wheat_disease_test_v1
python -m pip install -r requirements_test_v1.txt
$env:PYTHONPATH = ".\src"
python -m uvicorn wheat_demo_test_v1.api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs`. The response remains a demo contract until a separately validated real predictor is injected.

## File map

```text
cv_wheat_disease_test_v1/
|-- README_test_v1.md
|-- requirements_test_v1.txt
|-- src/wheat_demo_test_v1/
|   |-- __init__.py
|   |-- api.py
|   `-- service.py
`-- tests/test_service_contract_test_v1.py
```

## Provenance and boundary / 溯源与边界

- Test repository: `D:\工作流\portfolio`
- Legacy portfolio module: `D:\工作流\portfolio\projects\cv_wheat_disease`
- Original source label retained by the legacy module: `<local-source>/wheat-disease-demo`
- Knowledge source: `projects/cv_wheat_disease/src/knowledge/wheat_diseases.json`
- Source CSV / 来源 CSV: none identified; this module does not depend on CSV.
- No original code, model weight, screenshot, CSV, Excel, manifest, statistic, CLD, or frozen figure was modified.
