from __future__ import annotations

"""Scoped, read-only quality gate for current public portfolio surfaces.

Provenance: D:\\工作流\\portfolio at baseline a5a8e4012bc0a91d1d1eb81ce79d2605f0c6f186.
Source CSV: four paths under projects/stats_variance_correlation_pipeline/data/clean.
This gate never opens CSV/Excel/manifest contents, historical workflow JSON, or repository outputs.
"""

import ast
import json
import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
VISITOR_DOCS = (
    "README.md",
    "README.internship-test-v1.md",
    "docs/dataset_notes.md",
    "docs/methodology.md",
    "docs/provenance_correction_test_v1.md",
    "docs/system_overview.md",
    "docs/THIRD_PARTY_AND_ARTIFACT_POLICY_test_v1.md",
    "projects/cv_wheat_disease/PRODUCT_CASE_test_v1.md",
    "projects/comfyui_workflows/RECRUITER_SAFE_CASE_test_v1.md",
    "projects/comfyui_workflows/README.md",
    "projects/cv_wheat_disease_test_v1/README_test_v1.md",
    "projects/cv_wheat_disease/README.md",
    "projects/ml_training_pipeline/README.md",
    "projects/ml_training_pipeline/v2/README.md",
    "projects/stats_variance_correlation_pipeline/README.md",
    "projects/stats_variance_correlation_pipeline_test_v1/README_test_v1.md",
)
PROVENANCE_DOCS = (
    "README.internship-test-v1.md",
    "docs/THIRD_PARTY_AND_ARTIFACT_POLICY_test_v1.md",
    "projects/cv_wheat_disease/PRODUCT_CASE_test_v1.md",
    "projects/comfyui_workflows/RECRUITER_SAFE_CASE_test_v1.md",
    "projects/cv_wheat_disease_test_v1/README_test_v1.md",
    "projects/stats_variance_correlation_pipeline_test_v1/README_test_v1.md",
)
SAFE_JSON_FILES = (
    "projects/cv_wheat_disease/src/knowledge/wheat_diseases.json",
    "projects/ml_training_pipeline/v2/configs/train.json",
)
PYTHON_ROOTS = (
    REPO / "projects" / "cv_wheat_disease_test_v1",
    REPO / "projects" / "stats_variance_correlation_pipeline_test_v1",
    REPO / "tools",
)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def main() -> int:
    errors: list[str] = []
    checked_python = 0
    checked_json = 0
    checked_links = 0

    for relative in VISITOR_DOCS + SAFE_JSON_FILES:
        if not (REPO / relative).is_file():
            errors.append(f"missing required file: {relative}")

    for relative in VISITOR_DOCS:
        path = REPO / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if relative in PROVENANCE_DOCS and ("溯源" not in text or "来源 CSV" not in text):
            errors.append(f"document lacks provenance/source CSV statement: {relative}")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            checked_links += 1
            if not (path.parent / target).resolve().exists():
                errors.append(f"broken local link in {relative}: {raw_target}")

    for root in PYTHON_ROOTS:
        for path in sorted(root.rglob("*.py")):
            checked_python += 1
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError as exc:
                errors.append(f"python syntax error in {path.relative_to(REPO)}: {exc}")

    for relative in SAFE_JSON_FILES:
        path = REPO / relative
        if not path.is_file():
            continue
        checked_json += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON in {path.relative_to(REPO)}: {exc}")

    result = {
        "contract_version": "portfolio-v1",
        "read_only": True,
        "json_scope": list(SAFE_JSON_FILES),
        "checked_python_files": checked_python,
        "checked_json_files": checked_json,
        "checked_local_links": checked_links,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
