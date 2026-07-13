from __future__ import annotations

"""Static, read-only quality gate for the internship test-v1 branch.

Provenance: D:\\工作流\\portfolio at baseline a5a8e4012bc0a91d1d1eb81ce79d2605f0c6f186.
Source CSV: four paths under projects/stats_variance_correlation_pipeline/data/clean;
this gate checks paths and syntax but never opens CSV contents or writes repository files.
"""

import ast
import json
import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.internship-test-v1.md",
    "docs/internship_fit_assessment_test_v1.md",
    "docs/resume_alignment_test_v1.md",
    "docs/provenance_correction_test_v1.md",
    "docs/THIRD_PARTY_AND_ARTIFACT_POLICY_test_v1.md",
    "projects/cv_wheat_disease/PRODUCT_CASE_test_v1.md",
    "projects/comfyui_workflows/RECRUITER_SAFE_CASE_test_v1.md",
    "projects/cv_wheat_disease_test_v1/README_test_v1.md",
    "projects/stats_variance_correlation_pipeline_test_v1/README_test_v1.md",
)
NEW_DOCS = tuple(path for path in REQUIRED_FILES if path.endswith(".md"))
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

    for relative in REQUIRED_FILES:
        if not (REPO / relative).is_file():
            errors.append(f"missing required file: {relative}")

    for relative in NEW_DOCS:
        path = REPO / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if "溯源" not in text or "来源 CSV" not in text:
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

    for path in sorted(REPO.rglob("*.json")):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        checked_json += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON in {path.relative_to(REPO)}: {exc}")

    result = {
        "contract_version": "test-v1",
        "read_only": True,
        "checked_python_files": checked_python,
        "checked_json_files": checked_json,
        "checked_local_links": checked_links,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
