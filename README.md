# 余云兴｜Python & ML Engineering Portfolio

[![Portfolio quality](https://github.com/ax999617/portfolio/actions/workflows/portfolio-quality-test-v1.yml/badge.svg?branch=main)](https://github.com/ax999617/portfolio/actions/workflows/portfolio-quality-test-v1.yml)

面向 **Python 测试开发、机器学习质量与 AI 应用工程** 实习。本仓库重点展示可直接核验的工程能力：数据与模型契约、异常保护、API 边界、自动化测试和持续集成。

## 精选项目

| 项目 | 工程重点 | 可核验证据 |
|---|---|---|
| [ML Training Pipeline v2](projects/ml_training_pipeline/v2/README.md) | PyTorch 迁移学习骨架；显式类别、预处理与检查点契约；数据泄漏和恢复边界 | 6 个测试模块、22 个离线测试；仅使用合成图片和随机张量 |
| [Wheat Disease API Contract](projects/cv_wheat_disease_test_v1/README.md) | 完整图片解码、文件/像素上限、格式一致性、可注入推理后端和独立模拟模式 | 12 个服务层契约测试；真实后端错误失败关闭 |
| [Statistical Assets Read-only Gate](projects/stats_variance_correlation_pipeline_test_v1/README.md) | 来源文件存在性和遗留写入目标检查 | 2 个只读契约测试；不打开 CSV 内容，不运行统计或绘图 |

## 验证状态

- 本地验证：36 个测试通过（ML 22、CV 服务层 12、统计只读门禁 2）。
- GitHub Actions：持续验证静态质量、访客文档链接以及 CV/统计共 14 个测试。
- 详细测试范围、复现命令与尚未覆盖项见[证据与验证范围](docs/portfolio_evidence_v1.md)。

## 证据边界

本页只陈述能够由现有代码、测试或文档直接核验的结果。模型、统计、历史模块与第三方资产的详细边界见[证据与验证范围](docs/portfolio_evidence_v1.md)。

## 延伸阅读

- [证据与验证范围](docs/portfolio_evidence_v1.md)
- [数据与工件边界](docs/dataset_notes.md)
- [工程方法](docs/methodology.md)
- [仓库结构](docs/system_overview.md)
