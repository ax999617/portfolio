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
    "docs/README.md",
    "docs/dataset_notes.md",
    "docs/methodology.md",
    "docs/provenance_record.md",
    "docs/portfolio_evidence_v1.md",
    "docs/system_overview.md",
    "docs/asset_policy.md",
    "projects/cv_wheat_disease/PRODUCT_AND_RISK_CASE.md",
    "projects/comfyui_workflows/PUBLICATION_CHECKLIST.md",
    "projects/comfyui_workflows/README.md",
    "projects/comfyui_workflows/axstar_inpaint/README.md",
    "projects/comfyui_workflows/composite_pipeline/README.md",
    "projects/comfyui_workflows/noob_ai/README.md",
    "projects/comfyui_workflows/regional_anime/README.md",
    "projects/cv_wheat_disease_test_v1/README.md",
    "projects/cv_wheat_disease/README.md",
    "projects/ml_training_pipeline/README.md",
    "projects/ml_training_pipeline/v2/ALGORITHM_REFACTOR_REPORT.md",
    "projects/ml_training_pipeline/v2/README.md",
    "projects/misc_tools/README.md",
    "projects/stats_variance_correlation_pipeline/README.md",
    "projects/stats_variance_correlation_pipeline_test_v1/README.md",
    "projects/system_tools/README.md",
)
PROVENANCE_DOCS = (
    "docs/portfolio_evidence_v1.md",
    "docs/asset_policy.md",
    "projects/cv_wheat_disease/PRODUCT_AND_RISK_CASE.md",
    "projects/comfyui_workflows/PUBLICATION_CHECKLIST.md",
    "projects/cv_wheat_disease_test_v1/README.md",
    "projects/stats_variance_correlation_pipeline_test_v1/README.md",
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
FORBIDDEN_PUBLIC_PHRASES = {
    "README.md": ("not a raw file dump", "sanitized for publication"),
    "projects/comfyui_workflows/README.md": (
        "sanitized for publication",
        "reproducible generative pipelines",
    ),
}


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
        for phrase in FORBIDDEN_PUBLIC_PHRASES.get(relative, ()):
            if phrase.casefold() in text.casefold():
                errors.append(f"forbidden public phrase in {relative}: {phrase}")
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
        "checked_markdown_files": len(VISITOR_DOCS),
        "checked_local_links": checked_links,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
