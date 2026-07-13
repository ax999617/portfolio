from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import ProjectConfig
from .data import (
    DataContractError,
    ImageDecodeError,
    build_datasets,
    find_unreadable_images,
    supported_image_extensions,
)


def _supported_images(directory: Path) -> list[Path]:
    extensions = set(supported_image_extensions())
    try:
        return sorted(
            item
            for item in directory.rglob("*")
            if item.is_file() and item.suffix.lower() in extensions
        )
    except OSError:
        return []


def audit_dataset(data_root: str | Path, config: ProjectConfig) -> dict[str, Any]:
    """Classify dataset readiness without training, downloads, or source writes."""

    root = Path(data_root)
    report: dict[str, Any] = {
        "schema_version": 1,
        "source_root": str(root),
        "access_mode": "read_only",
        "layout": "missing",
        "source_complete": False,
        "training_ready": False,
        "class_contract": [
            {
                "slug": item.slug,
                "display_name": item.display_name,
                "source_directory": item.source_directory,
                "index": config.class_to_idx[item.slug],
            }
            for item in config.data.classes
        ],
        "issues": [],
        "recommended_action": "Provide an existing dataset directory.",
    }
    issues: list[dict[str, str]] = report["issues"]
    if not root.is_dir():
        issues.append({"code": "root_missing", "message": "Dataset root does not exist."})
        return report

    train_dir = root / "train"
    val_dir = root / "val"
    if train_dir.is_dir() or val_dir.is_dir():
        report["layout"] = "prepared_splits"
        try:
            build_datasets(root, config)
        except ImageDecodeError as exc:
            issues.append({"code": "unreadable_image", "message": str(exc)})
            report["recommended_action"] = (
                "Replace unreadable files in the prepared copy without changing the "
                "read-only source archive."
            )
            return report
        except (DataContractError, FileNotFoundError, OSError) as exc:
            issues.append({"code": "prepared_contract_failed", "message": str(exc)})
            report["recommended_action"] = (
                "Repair the prepared copy without changing the read-only source archive."
            )
            return report
        report["source_complete"] = True
        report["training_ready"] = True
        report["recommended_action"] = (
            "The prepared copy passes structural and exact-duplicate checks."
        )
        return report

    report["layout"] = "flat_source_archive"
    discovered = sorted(item.name for item in root.iterdir() if item.is_dir())
    expected = list(config.source_directory_to_slug)
    missing = sorted(set(expected) - set(discovered))
    extra = sorted(set(discovered) - set(expected))
    images_by_class = {
        name: _supported_images(root / name) for name in expected if name in discovered
    }
    empty = sorted(
        name for name in expected if name in discovered and not images_by_class[name]
    )
    unreadable = find_unreadable_images(
        (path for paths in images_by_class.values() for path in paths), root
    )
    report["present_source_directories"] = sorted(set(expected) & set(discovered))
    report["missing_source_directories"] = missing
    report["extra_source_directories"] = extra
    report["empty_source_directories"] = empty
    report["unreadable_images"] = unreadable
    if missing:
        issues.append(
            {
                "code": "missing_source_class",
                "message": "Missing source class directories: " + ", ".join(missing),
            }
        )
    if extra:
        issues.append(
            {
                "code": "unexpected_source_class",
                "message": "Unexpected source directories: " + ", ".join(extra),
            }
        )
    if empty:
        issues.append(
            {
                "code": "empty_source_class",
                "message": "Source class directories contain no supported images: "
                + ", ".join(empty),
            }
        )
    if unreadable:
        issues.append(
            {
                "code": "unreadable_image",
                "message": "Unreadable image files: " + ", ".join(unreadable[:10]),
            }
        )
    report["source_complete"] = not (missing or extra or empty or unreadable)
    report["recommended_action"] = (
        "Keep this archive read-only. Build a separate, provenance-preserving "
        "train/val/test copy grouped by capture source before any training."
        if report["source_complete"]
        else "Recover the missing source material; do not train on a reduced class contract."
    )
    return report
