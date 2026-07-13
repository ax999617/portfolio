# 文档溯源更正 - test v1

## 更正目的

原有 `docs/system_overview.md`、`docs/methodology.md` 和 `docs/dataset_notes.md` 形成于统计项目与 ML v2 加入之前，部分表述已经滞后。按照“不覆盖现有文件”的约束，本测试版新增更正页，不改写原文。

## 当前可验证状态

- 仓库已包含 `projects/stats_variance_correlation_pipeline/`。
- 仓库内有 4 个已跟踪 clean CSV 副本；因此“未发现来源 CSV”只适用于早期 CV/ML/ComfyUI 资产集，不能再作为整个仓库结论。
- ML v2 文档记录已找回完整三类平铺来源，但该来源未按 train/val/test 分组，仍是 `training_ready=false`。
- `projects/ml_training_pipeline/v2/` 是当前 ML 主阅读路径；上级目录的旧模型和权重仅为 `legacy/unverified`。
- 统计项目默认入口会写 catalog、报告和预览；在只读求职审查中不得直接执行。

## 来源 CSV

原始根：`D:\项目文件202605\制图数据`

- `data\clean\soil_core_variables_latest_long.csv`
- `data\clean\soil_core_variables_latest_v3_long.csv`
- `data\clean\soil_physicochemical_latest_v3_wide.csv`
- `data\clean\soil_physicochemical_latest_wide.csv`

仓库副本位于 `projects/stats_variance_correlation_pipeline/data/clean/`。本测试版只记录存在性与路径，不读取数值、不改写、不重算。

## 适用边界

- 原始仓库：`D:\工作流\portfolio`
- 基线提交：`a5a8e4012bc0a91d1d1eb81ce79d2605f0c6f186`
- 本文件不替代研究项目自身的 `source_asset_inventory.md`。
- 未修改 CSV、Excel、manifest、CLD、历史报告或冻结图。
