from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import torch
from PIL import Image
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.datasets.folder import IMG_EXTENSIONS
from torchvision.transforms import InterpolationMode

from .config import ProjectConfig


class DataContractError(ValueError):
    """Raised when a dataset does not match the explicit v2 contract."""


class ImageDecodeError(DataContractError):
    """Raised when a supported image file cannot be decoded safely."""


class ContractImageFolder(datasets.ImageFolder):
    """ImageFolder whose class order is supplied by configuration, not sorting."""

    def __init__(
        self,
        root: str | Path,
        class_names: Sequence[str],
        transform: transforms.Compose,
    ) -> None:
        self._contract_classes = tuple(class_names)
        super().__init__(str(root), transform=transform, allow_empty=False)

    def find_classes(self, directory: str) -> tuple[list[str], dict[str, int]]:
        discovered = sorted(entry.name for entry in Path(directory).iterdir() if entry.is_dir())
        expected = list(self._contract_classes)
        missing = sorted(set(expected) - set(discovered))
        extra = sorted(set(discovered) - set(expected))
        if missing or extra:
            raise DataContractError(
                f"Class directories in {directory} violate the contract; "
                f"missing={missing}, extra={extra}"
            )
        return expected, {name: index for index, name in enumerate(expected)}


@dataclass(frozen=True)
class DatasetBundle:
    train: ContractImageFolder
    val: ContractImageFolder
    test: ContractImageFolder | None


@dataclass(frozen=True)
class LoaderBundle:
    train: DataLoader
    val: DataLoader
    test: DataLoader | None
    train_generator: torch.Generator


def build_train_transform(config: ProjectConfig) -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.RandomResizedCrop(
                config.data.image_size,
                scale=(0.8, 1.0),
                ratio=(0.9, 1.1),
                interpolation=InterpolationMode.BILINEAR,
                antialias=True,
            ),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomApply(
                [transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1)],
                p=0.3,
            ),
            transforms.ToTensor(),
            transforms.Normalize(
                config.data.normalization_mean,
                config.data.normalization_std,
            ),
        ]
    )


def build_eval_transform(
    image_size: int,
    resize_size: int,
    mean: Sequence[float],
    std: Sequence[float],
) -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.Resize(
                resize_size,
                interpolation=InterpolationMode.BILINEAR,
                antialias=True,
            ),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean, std),
        ]
    )


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sample_records(
    datasets_by_split: dict[str, ContractImageFolder],
) -> list[tuple[str, str, Path]]:
    records: list[tuple[str, str, Path]] = []
    for split, dataset in datasets_by_split.items():
        for raw_path, target in dataset.samples:
            records.append((split, dataset.classes[target], Path(raw_path)))
    return records


def find_unreadable_images(
    paths: Iterable[str | Path], data_root: str | Path
) -> list[str]:
    """Return root-relative paths whose image payloads cannot be decoded."""

    root = Path(data_root).resolve()
    unreadable: list[str] = []
    for raw_path in paths:
        path = Path(raw_path)
        try:
            with Image.open(path) as image:
                image.load()
        except (OSError, SyntaxError, ValueError):
            try:
                display_path = path.resolve().relative_to(root).as_posix()
            except (OSError, ValueError):
                display_path = path.name
            unreadable.append(display_path)
    return sorted(unreadable)


def verify_decodable_images(
    datasets_by_split: dict[str, ContractImageFolder], data_root: str | Path
) -> None:
    unreadable = find_unreadable_images(
        (record[2] for record in _sample_records(datasets_by_split)), data_root
    )
    if unreadable:
        preview = ", ".join(unreadable[:10])
        raise ImageDecodeError("Unreadable image files: " + preview)


def verify_exact_duplicates(
    datasets_by_split: dict[str, ContractImageFolder],
    data_root: str | Path,
) -> None:
    """Reject byte-identical leakage across splits or contradictory class labels."""

    root = Path(data_root).resolve()
    by_size: dict[int, list[tuple[str, str, Path]]] = {}
    for record in _sample_records(datasets_by_split):
        by_size.setdefault(record[2].stat().st_size, []).append(record)

    violations: list[str] = []
    for records in by_size.values():
        if len(records) < 2:
            continue
        by_digest: dict[str, list[tuple[str, str, Path]]] = {}
        for record in records:
            by_digest.setdefault(_hash_file(record[2]), []).append(record)
        for digest, matches in by_digest.items():
            if len(matches) < 2:
                continue
            splits = {item[0] for item in matches}
            classes = {item[1] for item in matches}
            if len(splits) > 1 or len(classes) > 1:
                paths = [str(item[2].resolve().relative_to(root)) for item in matches]
                violations.append(
                    f"sha256={digest[:12]} splits={sorted(splits)} "
                    f"classes={sorted(classes)} paths={paths}"
                )

    if violations:
        preview = "\n".join(violations[:10])
        raise DataContractError(
            "Byte-identical images cross split or class boundaries:\n" + preview
        )


def build_datasets(data_root: str | Path, config: ProjectConfig) -> DatasetBundle:
    root = Path(data_root)
    if not root.is_dir():
        raise DataContractError(f"Dataset root does not exist: {root}")

    class_names = list(config.class_to_idx)
    train_dir = root / "train"
    val_dir = root / "val"
    test_dir = root / "test"
    if not train_dir.is_dir() or not val_dir.is_dir():
        raise DataContractError(
            f"Dataset must contain train/ and val/ directories under {root}"
        )

    try:
        train_dataset = ContractImageFolder(
            train_dir,
            class_names,
            transform=build_train_transform(config),
        )
        eval_transform = build_eval_transform(
            config.data.image_size,
            config.data.resize_size,
            config.data.normalization_mean,
            config.data.normalization_std,
        )
        val_dataset = ContractImageFolder(val_dir, class_names, transform=eval_transform)
        test_dataset = (
            ContractImageFolder(test_dir, class_names, transform=eval_transform)
            if test_dir.is_dir()
            else None
        )
    except FileNotFoundError as exc:
        raise DataContractError(f"A required class directory is empty: {exc}") from exc

    datasets_by_split = {"train": train_dataset, "val": val_dataset}
    if test_dataset is not None:
        datasets_by_split["test"] = test_dataset
    verify_decodable_images(datasets_by_split, root)
    if config.data.verify_cross_split_duplicates:
        verify_exact_duplicates(datasets_by_split, root)
    return DatasetBundle(train=train_dataset, val=val_dataset, test=test_dataset)


def build_contract_dataset(
    split_root: str | Path,
    class_names: Sequence[str],
    preprocessing: dict[str, object],
) -> ContractImageFolder:
    try:
        image_size = int(preprocessing["image_size"])
        resize_size = int(preprocessing["resize_size"])
        mean = tuple(float(item) for item in preprocessing["normalization_mean"])  # type: ignore[arg-type]
        std = tuple(float(item) for item in preprocessing["normalization_std"])  # type: ignore[arg-type]
    except (KeyError, TypeError, ValueError) as exc:
        raise DataContractError(f"Invalid preprocessing contract: {exc}") from exc
    if len(mean) != 3 or len(std) != 3:
        raise DataContractError("Preprocessing mean/std must contain three entries")
    transform = build_eval_transform(image_size, resize_size, mean, std)
    return ContractImageFolder(split_root, class_names, transform=transform)


def _seed_worker(_: int) -> None:
    worker_seed = torch.initial_seed() % (2**32)
    random.seed(worker_seed)


def _loader(
    dataset: ContractImageFolder,
    *,
    batch_size: int,
    shuffle: bool,
    num_workers: int,
    pin_memory: bool,
    generator: torch.Generator | None,
) -> DataLoader:
    kwargs: dict[str, object] = {
        "dataset": dataset,
        "batch_size": batch_size,
        "shuffle": shuffle,
        "num_workers": num_workers,
        "pin_memory": pin_memory,
        "worker_init_fn": _seed_worker,
        "generator": generator,
        "persistent_workers": num_workers > 0,
    }
    if num_workers > 0:
        kwargs["prefetch_factor"] = 2
    return DataLoader(**kwargs)


def build_loaders(
    datasets_bundle: DatasetBundle,
    config: ProjectConfig,
    device_type: str,
) -> LoaderBundle:
    generator = torch.Generator().manual_seed(config.training.seed)
    common = {
        "batch_size": config.training.batch_size,
        "num_workers": config.data.num_workers,
        "pin_memory": device_type == "cuda",
    }
    train_loader = _loader(
        datasets_bundle.train,
        shuffle=True,
        generator=generator,
        **common,
    )
    val_loader = _loader(
        datasets_bundle.val,
        shuffle=False,
        generator=None,
        **common,
    )
    test_loader = (
        _loader(
            datasets_bundle.test,
            shuffle=False,
            generator=None,
            **common,
        )
        if datasets_bundle.test is not None
        else None
    )
    return LoaderBundle(
        train=train_loader,
        val=val_loader,
        test=test_loader,
        train_generator=generator,
    )


def supported_image_extensions() -> Iterable[str]:
    return IMG_EXTENSIONS
