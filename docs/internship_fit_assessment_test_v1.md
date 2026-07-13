# 实习匹配评估 - test v1

## 结论

当前作品集与三份简历总体同源，但重点排序不够准确。求职优先级建议为：

1. **软件测试 / Python 测试开发 / ML 质量工程**：匹配度最高。仓库已有 6 个测试模块、22 个离线测试，覆盖失败关闭、数据泄漏、严格检查点、恢复与防覆盖。
2. **AI 应用开发 / Python / CV 工程**：匹配度中等。ML v2 工程证据较强，但小麦 Demo 没有真实模型，且仓库没有 RAG、Agent、部署或可观测性证据。
3. **AI 产品助理 / AIGC 工作流**：匹配度较低到中等。具备原型流程与工作流整理，但缺少真实用户研究、需求取舍记录、上线结果和可安全公开的完整 AIGC 案例。

## 简历与仓库契合度

| 简历版本 | 已被仓库支持的内容 | 原表述问题 | test v1 调整方向 |
|---|---|---|---|
| AI 应用开发 | Python、PyTorch/Torchvision、FastAPI、训练/评估/推理入口、数据与检查点契约 | 仍把旧 ResNet-18 原型放在首位；弱化了更强的 MobileNetV3 v2 与 22 个测试；“AI 应用”容易被误解为 LLM 应用 | 主项目改为 ML v2；明确真实训练未执行；CV 项目改称 API/风险/知识合同 Demo |
| 软件测试与工程实践 | v2 负向测试、合成 smoke、严格加载、防覆盖、CLI 失败路径；CV 输入校验 | 原简历只写“基础功能验证”，没有写出 6 模块/22 用例及具体缺陷类型 | 把 ML v2 质量工程放第一；补充 test-v1 CV 合同测试与 CI 门禁 |
| AI 产品与 AIGC | 4 类本地 ComfyUI 工作流整理、CV 用户流程、双语接口说明和免责声明 | 通用“提示词迭代”缺少仓库证据；旧 AIGC 文件含公开安全风险；缺用户/业务结果 | 删除无法直接核验的泛化表述；突出产品流程、验收、失败处理和安全发布门禁 |

## 仓库招聘就绪度

| 维度 | 基线判断 | test v1 处理 |
|---|---|---|
| 首屏定位 | 原 README 平均展示多个方向，主次不清 | 新增独立求职入口，按岗位给出 1 分钟阅读路径 |
| 工程可靠性 | ML v2 强；CV 和 stats 弱；无 CI | 新增 CV 无副作用服务合同、只读 stats 门禁与自动 CI |
| 可信边界 | 多数文档主动声明未重训，但 CV 旧 stub 和默认统计入口仍有风险 | test v1 不导入旧 patent stub，不把 mock 置信度当效果；stats 只检查不执行 |
| AIGC 安全 | 旧工作流和 PNG 元数据不适合直接招聘展示 | 从推荐路径移除，新增公开前安全门禁；不生成或伪造新案例 |
| 资产与许可 | 大权重、重复图片、第三方来源许可不完整 | 新增策略文档，明确 legacy/unverified 和“未授权即不复用” |

本地测试版验证结果为：ML v2 22/22、CV 合同 9/9、stats 只读门禁 2/2；静态门禁检查 7 个新增 Python 文件、13 个 JSON 和 9 个本地链接，无错误。上述结果只证明代码与合同行为，不代表模型效果或统计结论。

## 当前岗位基准

2026 年中国区官方岗位样本显示：

- AI 应用岗要求 Python/全栈基础、RAG 或 Agent、测试评测、错误处理、延迟/可观测性及生产部署；仅有模型调用或截图通常不够。[SAP AI Engineer Intern](https://jobs.sap.com/job/Shanghai-SAP-China-iXp-Interns-AI-Engineer-Intern-201203/1407267033/)、[Apple ML Engineer Intern](https://jobs.apple.com/en-us/details/200609538/machine-learning-engineer-intern-shanghai)
- AI 产品岗强调真实原型、非确定性问题调试、用户/业务问题、数据与事实型决策，而不仅是工具列表。[SAP AI Incubation Intern](https://jobs.sap.com/job/Beijing-iXP-Solution-Advisory-Intern-%28AI-Incubation%29-100016/1408612133/)、[Amazon 2026 Product Manager Intern](https://www.amazon.jobs/fr/jobs/3149572/senior-product-manager-intern-jst-2026)
- 测试岗已经明显偏测试开发：测试计划/框架、自动化、CI/CD、根因分析及性能质量是直接要求。[SAP Quality Engineer Intern](https://jobs.sap.com/job/XiAn-Shaanxi-SAP-China-iXp-Intern-Quality-Engineer-Xi%26apos%3Ban-710077/1397146933/)、[Amazon QAE Intern](https://www.amazon.jobs/en/jobs/3149135/quality-assurance-eng-intern-2026-beijing)
- 官方求职建议强调按 JD 定制、展示影响并附 GitHub，而不是罗列职责。[Adobe Hiring Process](https://careers.adobe.com/us/en/hiring-process)、[Microsoft University Internships](https://careers.microsoft.com/v2/global/en/universityinternship)

## 仍需本人补充的硬门槛

以下信息不能从仓库推断，不能由测试版代填：

- 预计毕业年月；
- 可开始实习日期、每周可到岗天数和可连续月数；
- 可接受城市或远程安排；
- 英语水平及可验证证据；
- 课程、竞赛、社团或真实协作经历中可公开的个人贡献。

这些字段在当前官方实习岗位中常是第一轮筛选条件，应在投递具体 JD 前补充。

## 不应使用的表述

- 不把 deterministic mock 写成“AI 识别准确率”或“真实模型推理”。
- 不把旧权重、旧训练曲线归因给 v2。
- 不写未实现的 RAG、Agent、SQL 项目或生产部署。
- 不写没有样本量、口径、来源和基线的指标。
- 不把候选 ComfyUI 图片说成已严格对应某个工作流。

## 溯源与边界

- 仓库：`D:\工作流\portfolio`，基线提交 `a5a8e4012bc0a91d1d1eb81ce79d2605f0c6f186`
- 简历：`C:\Users\man\Desktop\简历\余云兴_AI产品与AIGC版_简历.docx`、`余云兴_AI应用开发版_简历.docx`、`余云兴_软件测试与工程实践版_简历.docx`
- 统计原始根：`D:\项目文件202605\制图数据`
- 来源 CSV：`data\clean\soil_core_variables_latest_long.csv`、`soil_core_variables_latest_v3_long.csv`、`soil_physicochemical_latest_v3_wide.csv`、`soil_physicochemical_latest_wide.csv`（原始根下的相对路径）
- 本评估只使用静态审查与官方岗位页面；未重算统计、CLD、模型指标，未重画冻结图。
