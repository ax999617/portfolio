# 河南文化图像分类训练管线 v2

## 状态与目的

本目录是 `projects/ml_training_pipeline` 的独立重构版本。项目目的被收敛为：建立一个面向小样本、资源受限环境的三分类迁移学习候选管线，并让数据类别、预处理、模型结构、检查点和推理标签保持同一份可验证契约。

本次重构只新增代码、配置与合成测试，没有复制、修改或使用原始数据执行训练，也没有生成新的准确率、F1、能耗或量化结论。旧代码和旧权重保留在上级目录，仅作为历史归档；v2 不使用它们初始化模型。

完整三类来源现已在 `D:\识万物APP\henan_data` 找回；它仍是未经来源分组的类别平铺归档。本阶段继续采用保守策略：突出算法与可靠工程，不启动真实训练。完整分析见 [`ALGORITHM_REFACTOR_REPORT.md`](ALGORITHM_REFACTOR_REPORT.md)。

## 技术路线

- 骨干网络：ImageNet 预训练 `MobileNetV3-Small`，权重枚举固定为 `IMAGENET1K_V1`。
- 输入尺寸：192×192；相较 224×224，输入像素面积减少约 26.5%，但这不是实测能耗降幅。
- 默认训练：冻结特征骨干，只训练分类头；`finetune_epochs` 默认为 0。
- 可选微调：只有头部基线表现不足时，才解冻最后若干特征块，并为骨干和分类头使用不同学习率。
- 训练控制：AdamW、验证损失调度、早停、最佳检查点和可恢复的最后检查点。
- CUDA：可用时启用 `torch.amp`；CPU/MPS 自动禁用 AMP。
- 可靠性：固定随机种子、冻结 BatchNorm 统计量、训练前图像解码检查、严格检查点加载、显式类别顺序及跨分区字节级重复检测。
- 确定性恢复：默认 `num_workers=0`，使数据增强随机状态能够随检查点完整恢复；若为吞吐量改用多进程加载，必须同时关闭确定性模式并明确记录该取舍。
- 量化：暂不在 v2 中执行。只有浮点模型通过独立测试后，才应使用真实校准集评估静态 PTQ 或 QAT。

## 数据契约

先对任意来源运行只读审计；该命令不会训练或修改数据：

```powershell
$env:HENAN_DATA_ROOT = "<本机完整数据目录>"
python .\audit_dataset.py --data-root $env:HENAN_DATA_ROOT
```

当前完整来源会被识别为 `flat_source_archive`：`source_complete=true`，但由于没有 train/val/test 分区，`training_ready=false`。不要把原始目录直接传给训练入口。

数据必须预先按拍摄来源或采集批次划分，目录结构如下：

```text
dataset/
├── train/
│   ├── luoyang_peony/
│   ├── zhengzhou_bronze_artifact/
│   └── xinyang_maojian_tea_plant/
├── val/
│   └── <同样三个类别目录>/
└── test/                         # 可选；最终一次评估使用
    └── <同样三个类别目录>/
```

类别索引由 `configs/train.json` 的顺序唯一确定，不依赖 `ImageFolder` 的字典序：

```text
0 -> luoyang_peony
1 -> zhengzhou_bronze_artifact
2 -> xinyang_maojian_tea_plant
```

任一分区缺类、多类、空类或包含无法解码的图片都会失败。默认还会先按文件大小筛选候选，再计算必要的 SHA-256，拒绝跨 train/val/test 的字节完全相同图片，以及同一图片被赋予不同类别的情况。该检查不能发现裁剪、缩放或重新编码后的近重复图；近重复和同源序列仍需在数据整理阶段按组隔离。

## 安装与运行

在本目录创建独立环境后安装依赖：

```bash
pip install -r requirements.txt
```

当前代码在 Python 3.10.6、PyTorch 2.11 和 Torchvision 0.26 的 CPU 环境完成验证；依赖文件固定了 PyTorch/Torchvision 的兼容次版本。CUDA 环境应从 PyTorch 官方索引安装与本机驱动匹配的同版本构建。

先运行离线测试；测试不会下载预训练权重，也不会使用真实数据：

```bash
python -m unittest discover -s tests -v
```

在仓库根目录打开 PowerShell，进入 v2 目录，并把环境变量指向已经按来源分组且通过审计的数据副本：

```powershell
Set-Location .\projects\ml_training_pipeline\v2
$env:HENAN_PREPARED_DATA_ROOT = "<本机已分区数据目录>"
python .\train.py --data-root $env:HENAN_PREPARED_DATA_ROOT --device auto
```

首次真实训练若本机没有缓存官方 MobileNetV3-Small 权重，Torchvision 会下载该权重。输出默认写入 `runs/default/`，其中：

- `best.pt`：验证损失最优的严格检查点，用于最终测试和推理。
- `last.pt`：最后一个完整 epoch 的训练状态，用于中断恢复。
- `history.jsonl`：逐 epoch 的训练与验证记录。
- `summary.json`：最佳验证状态和可选测试集结果。

恢复中断训练时必须使用完全相同的配置：

```powershell
python .\train.py --data-root $env:HENAN_PREPARED_DATA_ROOT --resume .\runs\default\last.pt
```

独立评估与单图推理：

```powershell
python .\evaluate.py --checkpoint .\runs\default\best.pt --data-root $env:HENAN_PREPARED_DATA_ROOT --split test
python .\predict.py --checkpoint .\runs\default\best.pt --image "<本机待预测图片>"
```

如确认分类头基线欠拟合，可在新实验中把 `finetune_epochs` 从 0 调高；不要覆盖已有运行目录，并保留对应配置和检查点。

## 检查点契约

v2 检查点保存以下信息：

- schema 与管线版本；
- 模型架构、预训练权重标识和类别数量；
- `class_to_idx`、中文展示名和完整预处理参数；
- 配置指纹、训练阶段、epoch、最佳验证损失和早停状态；
- 模型、优化器、调度器、AMP scaler 与随机数状态。

模型参数使用 `strict=True` 加载；配置指纹、类别顺序、预处理或模型契约不一致时，恢复训练会立即失败。`best.pt` 还必须与 `last.pt` 记录的最佳 epoch 和验证损失一致，避免中断留下语义过期的最佳模型。不存在随机模型回退。

## 文件结构

```text
v2/
├── ALGORITHM_REFACTOR_REPORT.md
├── audit_dataset.py
├── configs/train.json
├── src/henan_v2/
│   ├── audit.py
│   ├── checkpoint.py
│   ├── config.py
│   ├── data.py
│   ├── engine.py
│   ├── metrics.py
│   └── models.py
├── tests/
├── train.py
├── evaluate.py
├── predict.py
└── requirements.txt
```

## 溯源

- 完整原始数据目录：`D:\识万物APP\henan_data`（只读，三类平铺归档）
- 不完整备份目录：`D:\乱七八糟存档\河南AI项目\henan_data`（只读，缺少信阳毛尖茶树）
- 历史原始项目根：`<local-source>/ml-training`
- 仓库内历史训练入口：`projects/ml_training_pipeline/src/train/train.py`
- 仓库内历史模型代码：`projects/ml_training_pipeline/src/models/trained.py`
- 仓库内历史量化代码：`projects/ml_training_pipeline/src/models/quantized.py`
- 历史权重：`projects/ml_training_pipeline/artifacts/weights/trained.pth`、`quantized.pth`、`quantized_model.pth`
- 参考图像：`assets/images/ml_training_pipeline/`
- 历史训练曲线：`assets/results/ml_training_pipeline/training_progress.png`
- 来源 CSV：未发现；v2 不依赖 CSV

上述 Windows 路径按项目溯源要求原样保留，只表示本次审计使用的只读来源，不是可移植的运行参数；公开命令使用环境变量，其他机器应指向各自的数据副本。

历史权重的分类头、模型结构和类别契约与当前旧代码存在冲突，因此它们被明确标记为 `legacy/unverified`，只作为早期模型结果展示，不作为 v2 的有效精度、量化或可复现推理证据。
