from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .catalog import REPRESENTATIVE_CODE_ASSETS, SELECTED_RESULT_ASSETS, SELECTED_SOURCE_DATASETS, SOURCE_SCAN_SUMMARY


def write_source_catalog(catalog_path: Path) -> Path:
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    source_root = Path(SOURCE_SCAN_SUMMARY["source_root"])
    payload = {
        "summary": SOURCE_SCAN_SUMMARY,
        "selected_source_datasets": [dataset.as_json(source_root) for dataset in SELECTED_SOURCE_DATASETS],
        "selected_result_assets": [asset.as_json(source_root) for asset in SELECTED_RESULT_ASSETS],
        "representative_code_assets": list(REPRESENTATIVE_CODE_ASSETS),
    }
    catalog_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return catalog_path


def _copy_file(source: Path, destination: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Missing asset source: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _find_pdftoppm() -> Path:
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        raise FileNotFoundError("pdftoppm was not found on PATH. Install Poppler or add it to PATH.")
    found = Path(pdftoppm)
    if found.suffix.lower() == ".exe":
        return found
    candidates = [
        found.parent / ".." / "native" / "poppler" / "Library" / "bin" / "pdftoppm.exe",
        found.parent / ".." / "Library" / "bin" / "pdftoppm.exe",
    ]
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.exists():
            return resolved
    return found


def _render_pdf_preview(pdf_path: Path, output_png: Path, log_path: Path, dpi: int = 200) -> None:
    output_png.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    pdftoppm = _find_pdftoppm()
    with tempfile.TemporaryDirectory(prefix="stats_pdf_render_") as tmp:
        tmp_dir = Path(tmp)
        tmp_pdf = tmp_dir / "input.pdf"
        tmp_prefix = tmp_dir / "preview"
        shutil.copy2(pdf_path, tmp_pdf)
        args = ["-png", "-singlefile", "-r", str(dpi), str(tmp_pdf), str(tmp_prefix)]
        if pdftoppm.suffix.lower() in {".cmd", ".bat"}:
            command = ["cmd", "/c", str(pdftoppm), *args]
        else:
            command = [str(pdftoppm), *args]
        env = os.environ.copy()
        env["PATH"] = str(pdftoppm.parent) + os.pathsep + env.get("PATH", "")
        completed = subprocess.run(command, capture_output=True, text=True, env=env)
        log_path.write_text(
            "\n".join(
                [
                    "command=" + " ".join(command),
                    f"source_pdf={pdf_path}",
                    f"returncode={completed.returncode}",
                    "stdout=" + completed.stdout.strip(),
                    "stderr=" + completed.stderr.strip(),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        if completed.returncode != 0:
            raise RuntimeError(f"pdftoppm failed for {pdf_path}. See {log_path}")
        rendered = tmp_prefix.with_suffix(".png")
        if not rendered.exists():
            raise FileNotFoundError(f"pdftoppm did not create expected preview: {rendered}")
        shutil.copy2(rendered, output_png)


def _asset_source(asset, source_root: Path, reference_dir: Path) -> tuple[Path, str]:
    source_candidate = asset.source_path(source_root)
    if source_candidate.exists():
        return source_candidate, "local_source"
    packaged_candidate = reference_dir / asset.packaged_name
    if packaged_candidate.exists():
        return packaged_candidate, "packaged_reference"
    return source_candidate, "missing"


def package_result_assets(
    source_root: Path,
    project_root: Path,
    output_dir: Path,
    render_previews: bool = True,
    refresh_reference_assets: bool = False,
) -> dict[str, object]:
    reference_dir = project_root / "reference_results" / "original"
    original_dir = output_dir / "result_assets" / "original"
    preview_dir = output_dir / "result_assets" / "previews"
    log_dir = output_dir / "logs"
    outputs: list[dict[str, object]] = []

    for asset in SELECTED_RESULT_ASSETS:
        selected_source, source_mode = _asset_source(asset, source_root, reference_dir)
        if source_mode == "missing":
            raise FileNotFoundError(f"Missing source and packaged reference for {asset.asset_id}: {selected_source}")

        reference_path = reference_dir / asset.packaged_name
        if refresh_reference_assets and source_mode == "local_source":
            _copy_file(selected_source, reference_path)

        output_original = original_dir / asset.packaged_name
        _copy_file(selected_source, output_original)

        preview_path: Path | None = None
        if render_previews:
            if asset.asset_type == "pdf":
                preview_path = preview_dir / f"{Path(asset.packaged_name).stem}.png"
                _render_pdf_preview(output_original, preview_path, log_dir / f"render_{asset.asset_id}.log")
            else:
                preview_path = preview_dir / asset.packaged_name
                _copy_file(output_original, preview_path)

        outputs.append(
            {
                "asset_id": asset.asset_id,
                "title": asset.title,
                "asset_type": asset.asset_type,
                "role": asset.role,
                "source_mode": source_mode,
                "original_source_path": str(asset.source_path(source_root)),
                "packaged_reference_path": str(reference_path),
                "output_original": str(output_original),
                "output_preview": str(preview_path) if preview_path else None,
                "notes": asset.notes,
            }
        )

    summary = {
        "pipeline": "stats_variance_correlation_pipeline",
        "source_root": str(source_root),
        "summary": SOURCE_SCAN_SUMMARY,
        "outputs": outputs,
        "boundaries": [
            "No historical CSV, Excel workbook, SAV file, manifest, CLD table, or frozen figure was modified.",
            "Frozen scientific PDFs were rendered only to PNG previews.",
            "Clean source CSV copies live under data/clean and are not overwritten by the default run.",
            "Optional variance/correlation computation is available only for explicitly supplied new data.",
        ],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "asset_package_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary
