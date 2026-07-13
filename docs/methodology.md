# Engineering and Documentation Method

## Evidence-first structure

The public portfolio is organized by what a visitor can verify, not by the amount of archived material:

1. **Current engineering projects** point to code, tests, and explicit failure behavior.
2. **Read-only evidence modules** expose provenance and safety boundaries without recalculation.
3. **Historical archives** remain available for traceability but are not presented as supported runtimes.

The recommended path is ML pipeline v2, the wheat service contract, and the statistical read-only gate. Legacy CV, ML weights, ComfyUI workflows, and Windows scripts are clearly separated from that path.

## Claim discipline

- Test results describe code behavior, not real-world model quality.
- Local source audits are labeled as local records rather than public dataset results.
- Historical outputs are not attributed to new code without a reproducible link.
- Missing training, deployment, HTTP, monitoring, dependency, and license evidence is stated directly.
- “Reproducible” is reserved for a scope with documented inputs, versions, commands, and output attribution.

## Verification layers

- Python AST parsing for current quality-gate roots.
- JSON parsing limited to two named current configuration/knowledge files.
- Markdown link checks limited to visitor-facing documents.
- 22 offline ML tests using synthetic images/tensors.
- 12 CV service-layer tests using decoded synthetic images and read-only knowledge JSON.
- 2 statistical gate tests that verify no output creation.

The FastAPI adapter is not yet covered by HTTP route tests. The CI workflow does not install PyTorch or run the 22 ML tests; those remain a documented local verification layer.

## Provenance and source CSV

- Source labels: `<local-source>/wheat-disease-demo`, `<local-source>/ml-training`, `<local-source>/comfyui/workflows`, `AutoHotkey v2 runtime`
- Statistical original root: `D:\项目文件202605\制图数据`
- Source CSV: `data\clean\soil_core_variables_latest_long.csv`, `soil_core_variables_latest_v3_long.csv`, `soil_physicochemical_latest_v3_wide.csv`, `soil_physicochemical_latest_wide.csv` under that root.
- This documentation review did not read or modify CSV/Excel/manifest contents and did not run statistics, CLD, training, report generation, or plotting.
