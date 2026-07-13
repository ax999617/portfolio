from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


class ConfigError(ValueError):
    """Raised when the v2 configuration violates its schema."""


_SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_]*$")


@dataclass(frozen=True)
class ClassSpec:
    slug: str
    display_name: str
    source_directory: str


@dataclass(frozen=True)
class DataConfig:
    image_size: int
    resize_size: int
    normalization_mean: tuple[float, float, float]
    normalization_std: tuple[float, float, float]
    classes: tuple[ClassSpec, ...]
    num_workers: int
    verify_cross_split_duplicates: bool


@dataclass(frozen=True)
class ModelConfig:
    architecture: str
    pretrained: bool
    pretrained_weights: str
    dropout: float


@dataclass(frozen=True)
class TrainingConfig:
    seed: int
    batch_size: int
    head_epochs: int
    finetune_epochs: int
    unfreeze_last_blocks: int
    head_learning_rate: float
    finetune_learning_rate: float
    finetune_head_learning_rate: float
    weight_decay: float
    label_smoothing: float
    early_stopping_patience: int
    early_stopping_min_delta: float
    scheduler_factor: float
    scheduler_patience: int
    amp: bool
    deterministic: bool


@dataclass(frozen=True)
class OutputConfig:
    directory: str
    best_checkpoint: str
    last_checkpoint: str
    history: str
    summary: str


@dataclass(frozen=True)
class ProjectConfig:
    schema_version: int
    provenance: Mapping[str, Any]
    data: DataConfig
    model: ModelConfig
    training: TrainingConfig
    output: OutputConfig
    fingerprint: str

    @property
    def class_to_idx(self) -> dict[str, int]:
        return {item.slug: index for index, item in enumerate(self.data.classes)}

    @property
    def display_names(self) -> dict[str, str]:
        return {item.slug: item.display_name for item in self.data.classes}

    @property
    def source_directory_to_slug(self) -> dict[str, str]:
        return {item.source_directory: item.slug for item in self.data.classes}

    @property
    def preprocessing_contract(self) -> dict[str, Any]:
        return {
            "image_size": self.data.image_size,
            "resize_size": self.data.resize_size,
            "normalization_mean": list(self.data.normalization_mean),
            "normalization_std": list(self.data.normalization_std),
        }


def _expect_keys(
    section: Mapping[str, Any],
    required: set[str],
    section_name: str,
    optional: set[str] | None = None,
) -> None:
    optional = optional or set()
    missing = required - set(section)
    unknown = set(section) - required - optional
    if missing:
        raise ConfigError(f"{section_name} is missing keys: {sorted(missing)}")
    if unknown:
        raise ConfigError(f"{section_name} has unknown keys: {sorted(unknown)}")


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ConfigError(f"{name} must be an object")
    return value


def _integer(value: Any, name: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ConfigError(f"{name} must be an integer >= {minimum}")
    return value


def _number(value: Any, name: str, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{name} must be numeric")
    result = float(value)
    if not math.isfinite(result) or result < minimum:
        raise ConfigError(f"{name} must be >= {minimum}")
    return result


def _boolean(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise ConfigError(f"{name} must be true or false")
    return value


def _triple(value: Any, name: str, *, positive: bool) -> tuple[float, float, float]:
    if not isinstance(value, list) or len(value) != 3:
        raise ConfigError(f"{name} must contain exactly three numbers")
    result = tuple(_number(item, name, 0.0) for item in value)
    if positive and any(item <= 0 for item in result):
        raise ConfigError(f"{name} entries must be > 0")
    return result  # type: ignore[return-value]


def _filename(value: Any, name: str, suffix: str) -> str:
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{name} must be a filename")
    path = Path(value)
    if path.name != value or path.suffix != suffix:
        raise ConfigError(f"{name} must be a local {suffix} filename")
    return value


def _parse_classes(value: Any) -> tuple[ClassSpec, ...]:
    if not isinstance(value, list) or len(value) < 2:
        raise ConfigError("data.classes must contain at least two classes")

    result: list[ClassSpec] = []
    for index, raw_item in enumerate(value):
        item = _mapping(raw_item, f"data.classes[{index}]")
        _expect_keys(
            item,
            {"slug", "display_name", "source_directory"},
            f"data.classes[{index}]",
        )
        slug = item["slug"]
        display_name = item["display_name"]
        source_directory = item["source_directory"]
        if not isinstance(slug, str) or not _SLUG_PATTERN.fullmatch(slug):
            raise ConfigError(f"data.classes[{index}].slug is not a safe class slug")
        if not isinstance(display_name, str) or not display_name.strip():
            raise ConfigError(f"data.classes[{index}].display_name must be non-empty")
        if (
            not isinstance(source_directory, str)
            or not source_directory.strip()
            or Path(source_directory).name != source_directory
        ):
            raise ConfigError(
                f"data.classes[{index}].source_directory must be one directory name"
            )
        result.append(
            ClassSpec(
                slug=slug,
                display_name=display_name.strip(),
                source_directory=source_directory,
            )
        )

    slugs = [item.slug for item in result]
    names = [item.display_name for item in result]
    source_directories = [item.source_directory for item in result]
    if len(slugs) != len(set(slugs)):
        raise ConfigError("data.classes contains duplicate slugs")
    if len(names) != len(set(names)):
        raise ConfigError("data.classes contains duplicate display names")
    if len(source_directories) != len(set(source_directories)):
        raise ConfigError("data.classes contains duplicate source directories")
    return tuple(result)



def load_config(path: str | Path) -> ProjectConfig:
    config_path = Path(path)
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"Cannot read configuration {config_path}: {exc}") from exc

    root = _mapping(raw, "config")
    _expect_keys(
        root,
        {"schema_version", "provenance", "data", "model", "training", "output"},
        "config",
    )
    schema_version = _integer(root["schema_version"], "schema_version", 1)
    if schema_version != 1:
        raise ConfigError(f"Unsupported config schema_version: {schema_version}")

    provenance = _mapping(root["provenance"], "provenance")

    data_raw = _mapping(root["data"], "data")
    _expect_keys(
        data_raw,
        {
            "image_size",
            "resize_size",
            "normalization_mean",
            "normalization_std",
            "classes",
            "num_workers",
            "verify_cross_split_duplicates",
        },
        "data",
    )
    image_size = _integer(data_raw["image_size"], "data.image_size", 96)
    resize_size = _integer(data_raw["resize_size"], "data.resize_size", image_size)
    data = DataConfig(
        image_size=image_size,
        resize_size=resize_size,
        normalization_mean=_triple(
            data_raw["normalization_mean"], "data.normalization_mean", positive=False
        ),
        normalization_std=_triple(
            data_raw["normalization_std"], "data.normalization_std", positive=True
        ),
        classes=_parse_classes(data_raw["classes"]),
        num_workers=_integer(data_raw["num_workers"], "data.num_workers", 0),
        verify_cross_split_duplicates=_boolean(
            data_raw["verify_cross_split_duplicates"],
            "data.verify_cross_split_duplicates",
        ),
    )

    model_raw = _mapping(root["model"], "model")
    _expect_keys(
        model_raw,
        {"architecture", "pretrained", "pretrained_weights", "dropout"},
        "model",
    )
    architecture = model_raw["architecture"]
    if architecture != "mobilenet_v3_small":
        raise ConfigError("model.architecture must be mobilenet_v3_small")
    pretrained_weights = model_raw["pretrained_weights"]
    if pretrained_weights != "MobileNet_V3_Small_Weights.IMAGENET1K_V1":
        raise ConfigError("model.pretrained_weights has an unsupported value")
    dropout = _number(model_raw["dropout"], "model.dropout", 0.0)
    if dropout >= 1.0:
        raise ConfigError("model.dropout must be < 1")
    model = ModelConfig(
        architecture=architecture,
        pretrained=_boolean(model_raw["pretrained"], "model.pretrained"),
        pretrained_weights=pretrained_weights,
        dropout=dropout,
    )

    train_raw = _mapping(root["training"], "training")
    _expect_keys(
        train_raw,
        {
            "seed",
            "batch_size",
            "head_epochs",
            "finetune_epochs",
            "unfreeze_last_blocks",
            "head_learning_rate",
            "finetune_learning_rate",
            "finetune_head_learning_rate",
            "weight_decay",
            "label_smoothing",
            "early_stopping_patience",
            "early_stopping_min_delta",
            "scheduler_factor",
            "scheduler_patience",
            "amp",
            "deterministic",
        },
        "training",
    )
    scheduler_factor = _number(
        train_raw["scheduler_factor"], "training.scheduler_factor", 0.0
    )
    if not 0.0 < scheduler_factor < 1.0:
        raise ConfigError("training.scheduler_factor must be between 0 and 1")
    label_smoothing = _number(
        train_raw["label_smoothing"], "training.label_smoothing", 0.0
    )
    if label_smoothing >= 1.0:
        raise ConfigError("training.label_smoothing must be < 1")
    training = TrainingConfig(
        seed=_integer(train_raw["seed"], "training.seed", 0),
        batch_size=_integer(train_raw["batch_size"], "training.batch_size", 1),
        head_epochs=_integer(train_raw["head_epochs"], "training.head_epochs", 1),
        finetune_epochs=_integer(
            train_raw["finetune_epochs"], "training.finetune_epochs", 0
        ),
        unfreeze_last_blocks=_integer(
            train_raw["unfreeze_last_blocks"], "training.unfreeze_last_blocks", 1
        ),
        head_learning_rate=_number(
            train_raw["head_learning_rate"], "training.head_learning_rate", 1e-12
        ),
        finetune_learning_rate=_number(
            train_raw["finetune_learning_rate"],
            "training.finetune_learning_rate",
            1e-12,
        ),
        finetune_head_learning_rate=_number(
            train_raw["finetune_head_learning_rate"],
            "training.finetune_head_learning_rate",
            1e-12,
        ),
        weight_decay=_number(train_raw["weight_decay"], "training.weight_decay", 0.0),
        label_smoothing=label_smoothing,
        early_stopping_patience=_integer(
            train_raw["early_stopping_patience"],
            "training.early_stopping_patience",
            1,
        ),
        early_stopping_min_delta=_number(
            train_raw["early_stopping_min_delta"],
            "training.early_stopping_min_delta",
            0.0,
        ),
        scheduler_factor=scheduler_factor,
        scheduler_patience=_integer(
            train_raw["scheduler_patience"], "training.scheduler_patience", 0
        ),
        amp=_boolean(train_raw["amp"], "training.amp"),
        deterministic=_boolean(
            train_raw["deterministic"], "training.deterministic"
        ),
    )
    if training.deterministic and data.num_workers != 0:
        raise ConfigError(
            "data.num_workers must be 0 when training.deterministic is true "
            "so checkpoint resume can restore the complete augmentation RNG state"
        )

    output_raw = _mapping(root["output"], "output")
    _expect_keys(
        output_raw,
        {"directory", "best_checkpoint", "last_checkpoint", "history", "summary"},
        "output",
    )
    output_directory = output_raw["directory"]
    if not isinstance(output_directory, str) or not output_directory.strip():
        raise ConfigError("output.directory must be a non-empty path")
    if Path(output_directory).is_absolute() or ".." in Path(output_directory).parts:
        raise ConfigError("output.directory must be a safe relative path")
    output = OutputConfig(
        directory=output_directory,
        best_checkpoint=_filename(
            output_raw["best_checkpoint"], "output.best_checkpoint", ".pt"
        ),
        last_checkpoint=_filename(
            output_raw["last_checkpoint"], "output.last_checkpoint", ".pt"
        ),
        history=_filename(output_raw["history"], "output.history", ".jsonl"),
        summary=_filename(output_raw["summary"], "output.summary", ".json"),
    )

    canonical = json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    fingerprint = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return ProjectConfig(
        schema_version=schema_version,
        provenance=dict(provenance),
        data=data,
        model=model,
        training=training,
        output=output,
        fingerprint=fingerprint,
    )
