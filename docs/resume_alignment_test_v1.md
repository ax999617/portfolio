# 简历与仓库证据映射 - test v1

## 使用方式

本文件记录三份求职测试版简历的改写依据。实际 DOCX 仅保存在本机简历目录，不提交含手机号和邮箱的副本到公开仓库。

## AI 应用开发版

优先证据：

- `projects/ml_training_pipeline/v2/`：MobileNetV3-Small、显式类别顺序、严格配置/检查点契约、原子保存、恢复训练、6 个测试模块和 22 个测试用例。
- `projects/cv_wheat_disease_test_v1/`：确定性 mock provider、输入限制、风险/知识/响应合同和自动化测试。
- `projects/stats_variance_correlation_pipeline/`：来源归档与可再计算边界；只作为数据工程附录。

改写原则：

- 用 v2 替换旧 ResNet-18/量化权重作为首要项目。
- 写清“测试证明工程实现，不代表真实模型效果”。
- 小麦项目称为“应用原型与服务合同”，不称为已接入真实 AI 模型。
- 移除无法从仓库核验的 SQL 强项表述。

## 软件测试与工程实践版

优先证据：

- `projects/ml_training_pipeline/v2/tests/`：22 个静态可数测试用例。
- `.github/workflows/portfolio-quality-test-v1.yml`：test-v1 质量门禁。
- `projects/cv_wheat_disease_test_v1/tests/`：正向、负向、边界与 provider 失败回退测试。
- `projects/stats_variance_correlation_pipeline_test_v1/`：只读检查与写入隔离。

改写原则：

- 不再只写“测试意识”，而写具体被拒绝的错误：缺类、坏图、跨分区重复、配置不一致、损坏检查点和重复输出目录。
- 不虚构覆盖率、缺陷数或性能结果。
- 将数据审计作为辅助项目，不把统计分析包装成软件测试。

## AI 产品与 AIGC 版

优先证据：

- `projects/cv_wheat_disease/PRODUCT_CASE_test_v1.md`：流程、验收、错误信息、免责声明和真实模型接入条件。
- `projects/comfyui_workflows/RECRUITER_SAFE_CASE_test_v1.md`：生成式工作流公开安全门禁。
- 原 `projects/comfyui_workflows/` 仅作为本地历史归档，不进入测试版推荐路径。

改写原则：

- 把“提示词迭代”改为可核验的需求拆解、流程说明、失败路径与发布审核。
- 不展示或链接含成人语义/敏感元数据的旧工作流与图片。
- 不虚构用户访谈、活跃用户、转化率或上线效果。

## 投递前人工确认

三份 DOCX 均应在每个具体 JD 下重新确认：目标岗位标题、毕业年月、实习起止时间、每周天数、城市与英语水平。当前来源没有这些事实，测试版不代填。

## 溯源与边界

- 原始简历根：`C:\Users\man\Desktop\简历`
- 原始仓库根：`D:\工作流\portfolio`
- 仓库基线：`a5a8e4012bc0a91d1d1eb81ce79d2605f0c6f186`
- 统计来源根：`D:\项目文件202605\制图数据`
- 来源 CSV：`data\clean\soil_core_variables_latest_long.csv`、`soil_core_variables_latest_v3_long.csv`、`soil_physicochemical_latest_v3_wide.csv`、`soil_physicochemical_latest_wide.csv`
- 本文件未修改或重新计算任何 CSV、Excel、manifest、统计、CLD、权重或冻结图。
