# Internship Portfolio - Test v1

> 求职测试版入口。原始 `README.md` 与现有项目文件保持不变；本页只重排招聘阅读路径，并把可验证证据与未完成边界放在同一处。

余云兴的 Python、机器学习工程、应用原型与质量验证作品集。当前最强证据不是“模型效果”，而是 `ml_training_pipeline/v2` 中的数据契约、严格检查点、失败关闭与离线测试，以及本测试版新增的无副作用 CV 服务合同与自动化验证。

## 一分钟阅读路径

| 优先级 | 项目 | 可直接核验的内容 | 诚实边界 |
|---|---|---|---|
| 1 | [ML Training Pipeline v2](projects/ml_training_pipeline/v2/README.md) | MobileNetV3-Small 迁移学习设计；类别/预处理/检查点单一契约；6 个测试模块、22 个测试用例 | 未用真实来源重新训练；没有新增准确率、F1、能耗或量化结论 |
| 2 | [CV API Refactor test v1](projects/cv_wheat_disease_test_v1/README_test_v1.md) | 无导入写盘副作用；确定性 mock provider；输入、风险、知识与响应合同；自动化负向测试 | 不是病害识别模型，不替代实验室检测或农技诊断 |
| 3 | [CV Product Case test v1](projects/cv_wheat_disease/PRODUCT_CASE_test_v1.md) | 用户流程、验收条件、错误路径、免责声明与下一步接入条件 | 只证明产品与接口设计，不证明模型效果 |
| 4 | [Stats Read-only Gate test v1](projects/stats_variance_correlation_pipeline_test_v1/README_test_v1.md) | 默认只检查来源和写入边界，不执行统计、CLD、绘图或报告重建 | 历史统计与冻结图不在本测试版重算 |
| 暂缓 | [AIGC Recruiter Safety Gate](projects/comfyui_workflows/RECRUITER_SAFE_CASE_test_v1.md) | 公开前的 prompt、模型名、图片元数据、依赖与许可审核规则 | 旧混合工作流不进入招聘推荐路径；本版未生成新工作流或新图片 |

## 按岗位阅读

### 软件测试 / Python 测试开发

1. `projects/ml_training_pipeline/v2/tests/`：数据缺类、坏图、跨分区重复、配置冲突、严格检查点、断点恢复和防覆盖。
2. `projects/cv_wheat_disease_test_v1/tests/`：上传校验、provider 回退、风险规则与响应合同。
3. `.github/workflows/portfolio-quality-test-v1.yml`：不接触真实数据的自动质量门禁。

### AI 应用开发 / Python 工程

1. `projects/ml_training_pipeline/v2/`：训练、评估、推理、恢复与失败关闭的完整工程骨架。
2. `projects/cv_wheat_disease_test_v1/`：把遗留随机 stub 隔离为明确的 mock provider，并保留未来真实模型依赖注入位置。
3. `projects/cv_wheat_disease/PRODUCT_CASE_test_v1.md`：接口为何存在、哪些结果必须拦截、何时才能接入真实模型。

当前仓库不包含可投递为核心卖点的 RAG、Agent 或生产部署项目，因此更适合 Python/CV 应用工程与 ML 质量方向，而不是把自己包装成大模型应用专家。

### AI 产品 / AIGC

1. `projects/cv_wheat_disease/PRODUCT_CASE_test_v1.md`：问题、用户流程、范围取舍、验收和风险提示。
2. `projects/comfyui_workflows/RECRUITER_SAFE_CASE_test_v1.md`：生成式工作流公开前的安全与可复现门禁。

该方向当前缺少真实用户研究、上线数据、业务结果和完整安全工作流，因此只建议投递重视原型、文档、工作流审计与跨职能协作的助理型岗位。

## 安全验证

以下命令只运行测试版的静态检查和临时目录测试，不读取真实训练数据，不重算统计或 CLD，不重画冻结图：

```powershell
python tools/portfolio_quality_gate_test_v1.py
python -m unittest discover -s projects/cv_wheat_disease_test_v1/tests -p "test*_test_v1.py" -v
python -m unittest discover -s projects/stats_variance_correlation_pipeline_test_v1/tests -p "test*_test_v1.py" -v
```

ML v2 的离线测试见其项目 README。它们使用临时合成图片和随机张量，不代表真实数据模型效果。

本地验证快照（2026-07-14）：

- ML v2：22/22 通过，Python 3.10.6、PyTorch 2.11.0 CPU、Torchvision 0.26.0；仅使用临时合成数据。
- CV test v1：9/9 通过，覆盖输入、mock、provider 回退、风险与响应合同。
- Stats read-only test v1：2/2 通过；4 个 CSV 与 3 个冻结资产仅检查存在性。
- 静态门禁：7 个新增 Python 文件、13 个 JSON、9 个本地 Markdown 链接，0 个错误。

## 已知限制

- 遗留 CV 项目的真实模型适配器未实现，旧 `qw.py` 包含结构 stub；招聘路径改用独立 test v1，不把模拟概率写成 AI 精度。
- 统计项目原默认入口会覆盖已跟踪 catalog/output 并重新渲染，本测试版不运行该入口。
- 旧 ComfyUI 混合归档含不适合招聘公开的文本和图片元数据；本入口不直接推荐这些文件。
- 遗留权重与重复图片仍为历史溯源资产；它们不作为当前可复现结果，也未在本测试版删除或改写。
- 未提供许可证即不等于允许第三方复用；详见 [第三方与工件策略](docs/THIRD_PARTY_AND_ARTIFACT_POLICY_test_v1.md)。

## 评估与简历映射

- [实习匹配评估](docs/internship_fit_assessment_test_v1.md)
- [简历与仓库证据映射](docs/resume_alignment_test_v1.md)
- [文档溯源更正](docs/provenance_correction_test_v1.md)

<details>
<summary>测试版溯源与数据边界</summary>

- 测试版仓库根：`D:\工作流\portfolio`
- 基线提交：`a5a8e4012bc0a91d1d1eb81ce79d2605f0c6f186`
- 简历来源根：`C:\Users\man\Desktop\简历`
- 统计原始根：`D:\项目文件202605\制图数据`
- 来源 CSV：
  - `D:\项目文件202605\制图数据\data\clean\soil_core_variables_latest_long.csv`
  - `D:\项目文件202605\制图数据\data\clean\soil_core_variables_latest_v3_long.csv`
  - `D:\项目文件202605\制图数据\data\clean\soil_physicochemical_latest_v3_wide.csv`
  - `D:\项目文件202605\制图数据\data\clean\soil_physicochemical_latest_wide.csv`
- 本测试版未修改上述 CSV、Excel、manifest、历史权重或冻结图；未重算统计、CLD 或模型指标。

</details>
