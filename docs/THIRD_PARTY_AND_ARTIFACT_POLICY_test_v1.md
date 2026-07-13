# 第三方与工件策略 - test v1

## 当前状态

仓库缺少统一许可证，部分模型权重、ComfyUI workflow、模型/LoRA/custom-node 名称和图片来源也没有完整公开许可链。因此测试版采用保守规则：**没有明确授权记录的资产，不等同于允许第三方复用。**

## 求职展示规则

- 遗留 `.pth` 只标记为 `legacy/unverified`，不作为 v2 可复现实验，也不建议继续直接分发。
- ComfyUI 旧混合归档不进入招聘推荐入口；恢复展示前必须完成 prompt、模型名、PNG 文本元数据、依赖版本和许可审查。
- 冻结科研图和 PDF 仅按现有溯源展示，不改图、不外推数值、不重新计算 CLD。
- 重复图片与大权重后续应迁移到明确许可的 Release/LFS 或外部工件存储；本测试版不删除历史文件，也不重写 Git 历史。
- 新增代码仅用于 test v1 演示与验证；合并到主分支前仍需由仓库所有者选择正式许可证。

## 发布清单

1. 记录资产原始路径、作者/来源和许可。
2. 检查 JSON、PNG/JPEG 文本元数据和隐藏 workflow/prompt。
3. 检查模型、LoRA、custom node 名称及其再分发条件。
4. 仅链接通过审核的样例；候选输出不得写成确定结果。
5. 对无法确认的资产默认不公开。

## 溯源与边界

- 仓库根：`D:\工作流\portfolio`
- ComfyUI 原始来源标识：`<local-source>/comfyui/workflows` 与 `<local-source>/comfyui/output`
- 统计原始根：`D:\项目文件202605\制图数据`
- 来源 CSV：`data\clean\soil_core_variables_latest_long.csv`、`soil_core_variables_latest_v3_long.csv`、`soil_physicochemical_latest_v3_wide.csv`、`soil_physicochemical_latest_wide.csv`
- 本策略没有修改或重新编码任何原资产，也没有声明未知第三方许可。
