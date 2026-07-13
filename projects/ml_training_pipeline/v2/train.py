from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn


V2_ROOT = Path(__file__).resolve().parent
SRC_ROOT = V2_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from henan_v2.checkpoint import (  # noqa: E402
    CheckpointError,
    build_checkpoint_payload,
    load_best_checkpoint,
    load_checkpoint,
    restore_model,
    restore_runtime_state,
    save_checkpoint_atomic,
    validate_checkpoint_against_config,
)
from henan_v2.config import ConfigError, ProjectConfig, load_config  # noqa: E402
from henan_v2.data import (  # noqa: E402
    DataContractError,
    build_datasets,
    build_loaders,
)
from henan_v2.engine import (  # noqa: E402
    TrainingError,
    create_grad_scaler,
    resolve_device,
    run_epoch,
    seed_everything,
)
from henan_v2.models import (  # noqa: E402
    build_model,
    configure_trainable_stage,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train the reliable, resource-aware Henan classifier v2."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=V2_ROOT / "configs" / "train.json",
        help="Path to the strict JSON configuration.",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        required=True,
        help="Root containing train/<class>, val/<class>, and optional test/<class>.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Override the configured output directory.",
    )
    parser.add_argument(
        "--resume",
        type=Path,
        help="Resume from a v2 last checkpoint with an identical configuration.",
    )
    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda", "mps"),
        default="auto",
    )
    parser.add_argument(
        "--head-only",
        action="store_true",
        help="Skip optional last-block fine-tuning even if configured.",
    )
    return parser.parse_args()


def _stage_plan(config: ProjectConfig, head_only: bool) -> list[dict[str, Any]]:
    stages: list[dict[str, Any]] = [
        {
            "name": "head",
            "epochs": config.training.head_epochs,
            "feature_lr": None,
            "head_lr": config.training.head_learning_rate,
        }
    ]
    if not head_only and config.training.finetune_epochs > 0:
        stages.append(
            {
                "name": "finetune",
                "epochs": config.training.finetune_epochs,
                "feature_lr": config.training.finetune_learning_rate,
                "head_lr": config.training.finetune_head_learning_rate,
            }
        )
    return stages


def _build_optimizer(
    model: nn.Module,
    stage: dict[str, Any],
    weight_decay: float,
) -> torch.optim.Optimizer:
    if stage["name"] == "head":
        groups = [
            {
                "params": [
                    parameter
                    for parameter in model.classifier.parameters()  # type: ignore[attr-defined]
                    if parameter.requires_grad
                ],
                "lr": stage["head_lr"],
            }
        ]
    else:
        feature_parameters = [
            parameter
            for parameter in model.features.parameters()  # type: ignore[attr-defined]
            if parameter.requires_grad
        ]
        head_parameters = [
            parameter
            for parameter in model.classifier.parameters()  # type: ignore[attr-defined]
            if parameter.requires_grad
        ]
        groups = [
            {"params": feature_parameters, "lr": stage["feature_lr"]},
            {"params": head_parameters, "lr": stage["head_lr"]},
        ]
    return torch.optim.AdamW(groups, weight_decay=weight_decay)


def _append_jsonl(path: Path, item: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")


def _write_json_atomic(path: Path, item: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    try:
        temporary.write_text(
            json.dumps(item, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    output_dir = (
        args.output_dir
        if args.output_dir is not None
        else (args.resume.parent if args.resume is not None else V2_ROOT / config.output.directory)
    ).resolve()
    if args.resume is not None and output_dir != args.resume.parent.resolve():
        raise ValueError("Resume output directory must be the checkpoint directory")
    best_path = output_dir / config.output.best_checkpoint
    last_path = output_dir / config.output.last_checkpoint
    history_path = output_dir / config.output.history
    summary_path = output_dir / config.output.summary
    if args.resume is None:
        existing = [
            path
            for path in (best_path, last_path, history_path, summary_path)
            if path.exists()
        ]
        if existing:
            raise ValueError(
                "Refusing to overwrite an existing run; use a new output directory: "
                + ", ".join(str(path) for path in existing)
            )

    device = resolve_device(args.device)
    seed_everything(config.training.seed, config.training.deterministic)

    datasets_bundle = build_datasets(args.data_root, config)
    loaders = build_loaders(datasets_bundle, config, device.type)
    stages = _stage_plan(config, args.head_only)

    if args.resume is not None:
        resume_checkpoint = load_checkpoint(args.resume)
        validate_checkpoint_against_config(resume_checkpoint, config)
        model = restore_model(resume_checkpoint, device)
        state = resume_checkpoint["training_state"]
        resume_stage_index = int(state["stage_index"])
        resume_stage_epoch = int(state["stage_epoch"])
        global_epoch = int(state["global_epoch"])
        best_val_loss = float(state["best_val_loss"])
        best_epoch = int(state["best_epoch"])
        resume_bad_epochs = int(state["bad_epochs"])
        if best_epoch < 1:
            raise CheckpointError("Resume checkpoint does not reference a valid best epoch")
        load_best_checkpoint(
            best_path,
            config,
            expected_best_epoch=best_epoch,
            expected_best_val_loss=best_val_loss,
        )
    else:
        resume_checkpoint = None
        model = build_model(
            num_classes=len(config.data.classes),
            pretrained=config.model.pretrained,
            dropout=config.model.dropout,
            architecture=config.model.architecture,
        ).to(device)
        resume_stage_index = 0
        resume_stage_epoch = 0
        global_epoch = 0
        best_val_loss = float("inf")
        best_epoch = 0
        resume_bad_epochs = 0

    if resume_stage_index >= len(stages):
        raise ValueError(
            "The resume checkpoint refers to a stage excluded by this invocation"
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    train_criterion = nn.CrossEntropyLoss(
        label_smoothing=config.training.label_smoothing
    )
    eval_criterion = nn.CrossEntropyLoss()
    for stage_index, stage in enumerate(stages):
        if stage_index < resume_stage_index:
            continue
        if stage_index > resume_stage_index:
            best_checkpoint = load_best_checkpoint(
                best_path,
                config,
                expected_best_epoch=best_epoch,
                expected_best_val_loss=best_val_loss,
            )
            model = restore_model(best_checkpoint, device)
            resume_checkpoint = None
            resume_stage_epoch = 0
            resume_bad_epochs = 0

        counts = configure_trainable_stage(
            model,
            stage=stage["name"],
            unfreeze_last_blocks=config.training.unfreeze_last_blocks,
        )
        optimizer = _build_optimizer(model, stage, config.training.weight_decay)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode="min",
            factor=config.training.scheduler_factor,
            patience=config.training.scheduler_patience,
        )
        scaler, amp_enabled = create_grad_scaler(device, config.training.amp)
        start_epoch = resume_stage_epoch if stage_index == resume_stage_index else 0
        bad_epochs = resume_bad_epochs if stage_index == resume_stage_index else 0
        if bad_epochs >= config.training.early_stopping_patience:
            start_epoch = int(stage["epochs"])

        if resume_checkpoint is not None and stage_index == resume_stage_index:
            checkpoint_stage = resume_checkpoint["training_state"]["stage"]
            if checkpoint_stage != stage["name"]:
                raise ValueError(
                    f"Checkpoint stage {checkpoint_stage!r} does not match {stage['name']!r}"
                )
            try:
                optimizer.load_state_dict(resume_checkpoint["optimizer_state_dict"])
                scheduler.load_state_dict(resume_checkpoint["scheduler_state_dict"])
                scaler.load_state_dict(resume_checkpoint["scaler_state_dict"])
            except (KeyError, RuntimeError, ValueError) as exc:
                raise ValueError(f"Cannot restore optimizer/runtime state: {exc}") from exc
            restore_runtime_state(resume_checkpoint, loaders.train_generator)

        for stage_epoch in range(start_epoch, int(stage["epochs"])):
            global_epoch += 1
            train_metrics = run_epoch(
                model=model,
                loader=loaders.train,
                criterion=train_criterion,
                device=device,
                num_classes=len(config.data.classes),
                optimizer=optimizer,
                scaler=scaler,
                amp_enabled=amp_enabled,
            )
            val_metrics = run_epoch(
                model=model,
                loader=loaders.val,
                criterion=eval_criterion,
                device=device,
                num_classes=len(config.data.classes),
            )
            val_loss = float(val_metrics["loss"])
            improved = val_loss < (
                best_val_loss - config.training.early_stopping_min_delta
            )
            if improved:
                best_val_loss = val_loss
                best_epoch = global_epoch
                bad_epochs = 0
            else:
                bad_epochs += 1
            scheduler.step(val_loss)

            record: dict[str, Any] = {
                "global_epoch": global_epoch,
                "stage": stage["name"],
                "stage_epoch": stage_epoch + 1,
                "train": train_metrics,
                "val": val_metrics,
                "learning_rates": [group["lr"] for group in optimizer.param_groups],
                "trainable_parameters": counts.trainable,
                "total_parameters": counts.total,
                "amp_enabled": amp_enabled,
                "device": str(device),
                "improved": improved,
            }
            _append_jsonl(history_path, record)
            print(json.dumps(record, ensure_ascii=False, sort_keys=True), flush=True)

            payload = build_checkpoint_payload(
                model=model,
                optimizer=optimizer,
                scheduler=scheduler,
                scaler=scaler,
                config=config,
                stage=stage["name"],
                stage_index=stage_index,
                stage_epoch=stage_epoch + 1,
                global_epoch=global_epoch,
                best_val_loss=best_val_loss,
                best_epoch=best_epoch,
                bad_epochs=bad_epochs,
                metrics={"train": train_metrics, "val": val_metrics},
                train_generator=loaders.train_generator,
            )
            if improved:
                save_checkpoint_atomic(payload, best_path)
            save_checkpoint_atomic(payload, last_path)
            if bad_epochs >= config.training.early_stopping_patience:
                break

        resume_checkpoint = None
        resume_stage_epoch = 0
        resume_bad_epochs = 0

    best_checkpoint = load_best_checkpoint(
        best_path,
        config,
        expected_best_epoch=best_epoch,
        expected_best_val_loss=best_val_loss,
    )
    best_model = restore_model(best_checkpoint, device).eval()
    test_metrics = None
    if loaders.test is not None:
        test_metrics = run_epoch(
            model=best_model,
            loader=loaders.test,
            criterion=eval_criterion,
            device=device,
            num_classes=len(config.data.classes),
        )
    summary = {
        "best_checkpoint": str(best_path),
        "best_epoch": best_epoch,
        "best_val_loss": best_val_loss,
        "class_to_idx": config.class_to_idx,
        "config_fingerprint": config.fingerprint,
        "test": test_metrics,
        "note": "test is null when no test/ split is supplied",
    }
    _write_json_atomic(summary_path, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CheckpointError, ConfigError, DataContractError, TrainingError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
