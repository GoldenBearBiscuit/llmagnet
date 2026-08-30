# AGENTS.md — LLMagnet 项目上下文(给在新机器上打开本仓库的 agent)

> 你(agent)正在接手一个进行中的项目。本文件是从一段长架构对话中沉淀的完整上下文。
> 读完后:当前任务是 **在云机上执行 mvp/RUNBOOK.md 的 Phase 0**。

## 文档地图(按序阅读)

1. `docs/PRD.md` — 项目定义、前因后果、16 条用户决策日志、里程碑与红线
2. `docs/CONVERSATION_LOG.md` — 22 轮对话完整纪要(每个结论的原始推理与文献链接)
3. `mvp/PLAN.md` — MVP 实验方案(四假设/四阶段/预算)
4. `mvp/RUNBOOK.md` — 云机部署执行手册(当前要执行的)
5. `paper/OUTLINE.md` — 论文规划(投稿策略/贡献声明/图表清单);`paper/references.bib` 文献库
6. `README.md` — 框架总体架构与目录说明

## 项目一句话

LLMagnet = 「输入开源权重 LLM + 现成 agent → 输出隐空间 agent」的编译器框架。
MVP 阶段用 Qwen2.5-1.5B + dsh(DeepSeek Harness)agent,在单卡 3090 云机上逐个验证 4 个核心假设。

## 当前状态(截至 2026-08-30)

- ✅ 架构论证完成,结论全部沉淀在 `mvp/PLAN.md`(必读)
- ✅ Phase 0 代码全部就位:`mvp/dsh-plugin`(JS 工具插件 + cordis.yml)、`mvp/harness`(runner_dsh.py + judge.py)、`mvp/tasks`(kb + 300 训练 + 50 封存金标 + 5 冒烟,种子 20260830,答案已独立验算)
- ✅ 五个参考组件浅克隆在 `refs/`(agent-lightning / LatentMAS / coconut / Mage / mem0;Phase 0 不需要它们,Phase 1 起按需重克隆即可)
- ⏳ **下一步:云机执行 `mvp/RUNBOOK.md` 步骤 ①-⑧**(vLLM 起 Qwen → dsh 挂插件 → 冒烟 5 条 → 300 任务基线)

## 四个核心假设(所有实验的主线)

| # | 假设 | 对应大框架部件 | 验收 |
|---|---|---|---|
| H1 | 明文 CoT → 隐循环,质量不降 token 大降 | forge/distill(-O1) | 质量 ≤2% 掉幅,token -30% |
| H2 | "要不要调工具"隐状态线性可读 | rt/gate(触发层) | 探针 F1 ≥ 0.8 |
| H3 | 工具结果编码回隐状态不劣化 | rt/fork_exec(-O2) | ≥ 明文注入的 95% |
| H4 | 可验证奖励 RFT/GRPO 越调越准 | forge/trainer(-O3) | 3 轮成功率单调升 |

证伪也是有效结果,写进 `mvp/reports/` 并回头修订架构。

## 硬性红线(违反即返工)

1. guardrails/安全层永不编译进隐空间(机器人场景是物理安全要求)
2. 外部锚(冻结金标集 golden_50、奖励函数)对训练侧只读,修改权在人类
3. 明文只允许出现在 fork 边界与最终答案;fork 边界同时是审计日志
4. 自产数据占比有上限(manifest: 0.5),真实流量/物理反馈必须持续注入
5. manifest.yaml 锁能力边界:底模血统、任务分布、工具 schema 版本

## 关键架构事实(论证过,别重新发明)

- agent 用 **dsh**(用户指定,"一切皆插件"):工具 = JS defineTool 插件;模型 = vLLM 起 OpenAI 兼容端点,dsh 经 llm-pi-ai 自定义 route 指向;驱动 = deepseek-harness-sdk(自带捆绑 runtime,**无需安装 Node.js**)
- dsh 处于开发者预览期,cordis 组合格式可能变——排障参照 `dsh/examples/headless-agent/cordis.yml`(若机器上没有,从本地上传)
- 隐空间方案的文献坐标:Coconut(H1 蒸馏配方)、LatentMAS(零训练隐循环)、arXiv:2605.14038(工具意图线性可读)、ICAE/RCC(fork 回注压缩)、Absolute Zero + Darwin Gödel Machine(自进化先例)、Agent Lightning(RL 训练范式)
- 本机工作区 `D:\Project\dsh` 是 dsh 源码仓库,排障时本地查,云机不用克隆整个 dsh

## 工作方式约定

- 每个阶段结束在 `mvp/reports/` 写一页:假设 → 数字 → 结论(成立/证伪/存疑)
- traces 和失败案例永远保留(它们是探针训练数据和评测集种子)
- 预算上限 ¥6000;核心 ~¥150,扩展实验菜单见 PLAN §6,按结果挑选,不预支
- 金标集 golden_50.jsonl 封存:不参与任何调参/训练决策
