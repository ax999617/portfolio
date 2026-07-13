# 作品集证据与验证范围（v1）

本页记录公开首页中各项技术表述的证据范围与已知限制。面向访客的主要入口请见[仓库首页](../README.md)。

## 证据总览

| 项目 | 已验证内容 | 当前不声明的内容 |
|---|---|---|
| [ML Training Pipeline v2](../projects/ml_training_pipeline/v2/README.md) | 22 个离线测试；类别、配置、数据审计、严格检查点、恢复入口与防覆盖 | 真实来源模型精度、量化收益、生产延迟或能耗 |
| [Wheat Disease API Contract](../projects/cv_wheat_disease_test_v1/README.md) | 12 个服务层测试；图片解码、大小/像素限制、格式一致性、provider 合同和失败关闭 | 真实病害识别精度、HTTP 端点自动化测试、生产部署 |
| [Statistical Assets Read-only Gate](../projects/stats_variance_correlation_pipeline_test_v1/README.md) | 2 个只读测试；4 个 CSV 路径和 3 个冻结资产只检查存在性 | CSV 内容正确性、统计结论、CLD 或图表再现 |

## 验证命令

以下命令不运行真实训练、统计、CLD、报告生成或绘图：

```powershell
python tools/portfolio_quality_gate_test_v1.py
python -m unittest discover -s projects/cv_wheat_disease_test_v1/tests -p "test*_test_v1.py" -v
python -m unittest discover -s projects/stats_variance_correlation_pipeline_test_v1/tests -p "test*_test_v1.py" -v
```

ML v2 的 22 个测试需要 PyTorch/Torchvision，测试数据均为临时合成内容。当前总计 36 个本地测试；GitHub Actions 的轻量范围运行其中 14 个，并额外检查 Python 语法、2 个指定 JSON 和访客文档链接。

## 历史模块与公开边界

- [旧 CV 模块](../projects/cv_wheat_disease/README.md)保留早期接口和截图，只作为溯源归档。
- [旧 ML 模块](../projects/ml_training_pipeline/README.md)的权重和量化工件为 `legacy/unverified`，v2 不加载它们。
- [旧统计模块](../projects/stats_variance_correlation_pipeline/README.md)会写入已跟踪输出，因此不作为默认运行入口。
- [ComfyUI 归档](../projects/comfyui_workflows/README.md)未通过完整公开发布审核，不作为核心项目。

## 数据与许可

- 统计来源文件仅做路径存在性检查；本次未读取其数值。
- 无统一仓库许可证时，不应推断历史权重、workflow、图片或第三方组件可被复用。
- 详细边界见[数据说明](dataset_notes.md)和[第三方与工件策略](asset_policy.md)。

<details>
<summary>溯源记录与来源 CSV</summary>

- 仓库工作根：`D:\工作流\portfolio`
- 本页最初形成于求职材料审查；简历来源根：`C:\Users\man\Desktop\简历`。当前展示审查未修改简历。
- 统计原始根：`D:\项目文件202605\制图数据`
- 来源 CSV：
  - `D:\项目文件202605\制图数据\data\clean\soil_core_variables_latest_long.csv`
  - `D:\项目文件202605\制图数据\data\clean\soil_core_variables_latest_v3_long.csv`
  - `D:\项目文件202605\制图数据\data\clean\soil_physicochemical_latest_v3_wide.csv`
  - `D:\项目文件202605\制图数据\data\clean\soil_physicochemical_latest_wide.csv`
- 未修改 CSV、Excel、manifest、统计、CLD、历史权重或冻结图。

</details>
