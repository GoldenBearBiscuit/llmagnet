# LLMagnet 对话纪要(完整导出)

> 记录 2026-08-30 一天内从「AI memory 调研」到「可执行 MVP 仓库」的全部推演过程。
> 本文件是决策日志的原始推理版;结论版见 docs/PRD.md 的决策日志表。

---

## 第 1 轮:AI memory 框架全景调研

**问**:目前 AI memory 框架有什么发现?跑分最高的哪个?路线有几条?最出名?工业上最多用?

**查证与结论**:
- 主流基准:LoCoMo(1,540 题,争议大)、LongMemEval(公认金标准)、ConvoMem。
- 自报头部数字:Mem0(LongMemEval ~94)、Supermemory(自评三榜第一)、Mastra(94.87%)、MemOS(LoCoMo +38.9%,时序推理 +159%)、Letta filesystem 74%、Zep 官方 84% 但第三方复测 58.44%。
- **跑分大战**:Mem0 与 Zep 互发檄文(《Lies, Damn Lies & Statistics》),MemOS 提出 ABC 基准规范;第三方横评结论"none wins"。
- 技术路线三分法(存储介质):**外置/上下文**(主流,内分扁平抽取式/知识图谱式/文件系统式/分层 OS 式)、**参数化**(权重内)、**潜空间**(隐状态)。
- 最出名:学术 MemGPT(奠基论文),生态 Mem0(~64k star)。
- 工业最多用:开源侧 Mem0;企业重时序/审计用 Zep;绝对用户量是 ChatGPT/Claude/Gemini 自带记忆(闭源自研)。

关键链接:mem0.ai/blog/state-of-ai-agent-memory-2026 · letta.com/blog/benchmarking-ai-agent-memory · blog.getzep.com(檄文) · github.com/getzep/zep-papers#5

## 第 2 轮:三巨头深挖(Mem0 / MemGPT / Zep)

**问**:这三个比较引人注意,细看。

**查证与结论**(对应三种架构哲学):
- **Mem0** = 记忆 API:两阶段管道(抽取显著事实 → ADD/UPDATE/DELETE/NOOP 冲突消解)存向量库;图谱变体 Mem0g 只 +2% 但延迟大。
- **MemGPT→Letta** = 记忆操作系统:LLM 即 OS,上下文=内存/外部=磁盘;memory blocks 自编辑;sleep-time compute(做梦整理记忆);"纯文件系统就够"实测 LoCoMo 74%。
- **Zep/Graphiti** = 企业记忆:三层子图 + **双时态**(世界有效时间 × 系统得知时间),矛盾事实不覆盖历史。
- 跑分争议核心:Mem0 论文报 Zep 36% → Zep 反驳 → 第三方复测 Zep 58.44%(低于其自称 84%)。
- 选型:快接入→Mem0;全托管 agent/多 agent 共享→Letta;事实会变+审计→Zep。

关键链接:arxiv.org/abs/2504.19413(Mem0) · arxiv.org/abs/2501.13956(Zep) · arxiv.org/abs/2310.08560(MemGPT)

## 第 3 轮:内置到 LLM 里的记忆(参数化/潜空间)

**问**:这些都是外置的,还有一大类内置到 LLM 里的,搜一下。

**查证与结论**(内置三方向):
1. **参数化**:ROME(秩一编辑)→ MEMIT(批量)→ WISE(NeurIPS 2024,主存+侧存+路由)→ GRACE(微软,数千次连续编辑);2025-26 新趋势:agent 经验回写权重(TMEM 等)。
2. **潜空间**:MemoryLLM(自更新记忆池)→ M+(ICML 2025,检索 memory tokens);**Titans**(Google,NeurIPS 2025,测试时记忆,surprise 门控,2M+ 上下文)。
3. **记忆层**:Meta FAIR Memory Layers at Scale(128B 记忆参数/1T token,product-key 查找,事实任务超 MoE)。
- 工业现状:外置 99%;知识编辑用于修事实错误;Titans/记忆层塑造下一代基座。
- 为什么工业不用内置:动模型本体、不可审计、多租户隔离难、无法回滚删除(隐私合规硬伤)。

关键链接:arxiv.org/abs/2501.00663(Titans) · arxiv.org/abs/2412.09764(Meta) · research.google/blog/titans-miras

## 第 4 轮:用户的"四合一"设想(项目创意诞生)

**用户原话要点**:① Fable5 有前空间试探路线;② 取消明文思考只在最后一步映射成文字;③ 前空间及一层(这一层返回来就是前空间触发层);④ 微软 Mage-VL 实时视频技术——四合一。

**查证与评估**:
- "Fable5" = Anthropic 2026 旗舰(Claude Fable 5 & Mythos 5 系统卡):**J-space/全局工作空间**(中间层共享潜空间,推理静默完成)+ **illegible reasoning**(不可读推理,延迟降 4.4×)——是"观察到的现象",非公开机制。
- 组件② Coconut/Soft Thinking/RoT/CoLT/BAAI 潜空间推理综述(带宽 2700×)——文献已铺好。
- 组件④ Mage-VL:codec-native(不解码帧直接吃码流,视觉 token -75%)、流式、4B 开源。
- **评估**:组合自洽(四块同攻"文字是低带宽接口");**触发层最原创**(Coconut 无记忆、Titans 有门控非循环入口、Mage-VL 无推理、Anthropic 只观察)——四合一 = 把 J-space 现象做成显式可训练机制。
- **三大坑**:训练信号(无明文 CoT 可监督)、触发策略(RL)、可审计性归零。

关键链接:anthropic.com/research/global-workspace · Fable5/Mythos5 系统卡 PDF · arxiv.org/abs/2607.24904(Mage-VL)

## 第 5 轮:Mage-VL 的记忆管理

**问**:搜一下 Mage-VL 的记忆是如何管理的。

**论文精读结论**(arXiv 2607.24904):
1. 流式感知记忆 ℳper:EPFE 循环状态,**只给 cognition gate 做 silent/speak 决策用**;
2. 生成时明确放弃长程记忆("we do not employ complex long-range memory for language generation"),只用最近 N 个 codec 段滑窗;
3. 滚动码流 token 窗口(锚定帧稠密/预测帧稀疏,3D RoPE);
4. **没有** KV cache 管理/分层记忆/整合/淘汰策略——靠 codec 稀疏性(75% 减量)+ 门循环状态替代。

**对项目的意义**:Mage-VL 的 gate = 用户"触发层"的原始雏形,但**无记忆、无回写**;四合一的差异化空间正好在这。

## 第 6 轮:终极目标确认(隐空间触发 agent + 最后映射文字)

**用户原话要点**:最终想达到:可以在隐空间触发 agent 功能,只有拿到答案再映射成文字。

**查证与结论**(逐环节文献验证,全部有先例):
- 工具意图在隐状态**线性可读**(arXiv:2605.14038,生成工具调用 token 之前)→ 触发层假设成立;
- Agent 全隐空间协作:Interlat(隐状态直传,跨异构模型)、**LatentMAS**(ICML 2026 Spotlight,training-free,隐嵌入覆盖文本嵌入空间);
- 停止判定:PonderNet/ACT 可学停顿先例;
- 两个打折点:①工具参数必须落地文本(外部接口),但贵的部分是调用之间的思考;②**文本安全不迁移到工具调用安全**(arXiv:2602.16943),全隐轨迹审计只剩工具日志+答案。

## 第 7 轮:fork 方案(工具 I/O 不落地)

**用户原话要点**:工具参数虽是明文,但调用时 fork 一下,工具完成后编码,这条分支最后的结果跟 CoT 不落地一样传回去,对触发的 main 来说还是不落地的。

**结论**:成立,且是"CoT 不落地"到"工具 I/O 不落地"的正确推广(明文=传输编码)。回注三档:
- A 直接 encode(零训练,LatentMAS 证据);
- B 压缩器:ICAE(arXiv:2307.06945)/ Gist(arXiv:2304.08467)/ RCC(arXiv:2406.06110)/ 500xCompressor,LoRA 只训压缩器;
- C 侧分支自持明文 KV + cross-attention / 写神经记忆。
额外好处:主循环上下文不膨胀;fork 边界天然留审计日志;多模态结果直接进 latent。SPORK 指出 agentic 推理 35-50% token 浪费在重复解码工具调用体。

## 第 8 轮:Agent Lightning 调研

**问**:搜一下 Agent Lightning(微软智能体强化学习开源框架)。

**结论**:"Train ANY AI Agents with RL",首个 agent 执行与 RL 训练完全解耦的框架:
- Lightning Server(训练控制器,OpenAI 兼容端点供新权重)+ Lightning Client(agent 运行时,任意框架零改动);
- 数据:任意 agent 运行归约成 transitions(输入,输出,奖励),训练器不懂 agent 内部;
- LightningRL:层级 credit assignment(现实现:episode 内均分回报)+ 复用 PPO/GRPO/REINFORCE++;
- **AIR**(Automatic Intermediate Rewarding):工具状态→中间奖励,对抗稀疏;
- 实验:Llama-3.2-3B 在 LangChain/OpenAI Agents SDK/AutoGen 三框架验证。

关键链接:arxiv.org/abs/2508.03680 · github.com/microsoft/agent-lightning

## 第 9 轮:用场景讲明白 Agent Lightning

**场景**:退款客服 agent(查订单→判断政策→退款,一次任务 4 次 LLM 调用)。
- RL = 让 agent 跑 1 万单、按成败打分、调权重;
- 传统痛点:训练框架要求 agent 跑在内部 = "拆车装进驾校模拟器";
- Agent Lightning = "驾校搬进车里":训练器伪装成 LLM API,顺手记录每次调用;任务结束按结果回填分数;
- 均分功劳 = 小组奖金平均分(粗糙但能用);AIR = 教练中途拍肩。

## 第 10 轮:越调越准 + "不可拆"辨析

**问**:隐空间调 agent 用这框架会越调越准?那 LLM+agent 就是不可拆集合了?

**结论**:
- 对,但精确化:框架直接能训的是**落地文本部分**(工具调用/答案);纯隐决策要按范式自建训练循环(触发/停止当 action,工具状态当 AIR 奖励);
- 越调越准的前提是奖励设计,否则 reward hacking(挑简单题/回避难工具);
- "不可拆"对一半:**行为沉进权重**(触发策略/工具意图/推理习惯与模型长在一起,换底模=重训,改行为=训练而非改 prompt)= 不可拆;训练器/记忆/工具依然可拆。行业趋势 = 脚手架 → 权重内。

## 第 11 轮:做成框架?有绝对优势吗?

**结论**:
- 能:形状 = Agent Lightning(文本版)再加三个编译 pass,设计成**带优化等级的 agent 编译器**(-O0 基线 / -O1 隐循环 / -O2 fork / -O3 RL),每级独立可回退;硬前提:开源权重;
- **无绝对优势,只有条件优势**:赢在实时流(视频/机器人,唯一结构性必需)、长链高并发(SPAROK:35-50% token 浪费)、多 agent 带宽;输在峰值推理质量(明文 CoT 是纠错通道,Coconut 部分任务输给明文)、通用性(编译产物绑定任务分布)、优势窗口随基模变快收窄。
- 定位:特定场景专用编译器,验收 = "同任务集延迟/成本降 X 倍、质量不降",不打智力榜。

## 第 12 轮:框架做出来什么样

**产出**:构建时(forge:tracer/distill/fork/trainer/verify)+ 运行时(rt:loop/gate/fork_exec/memory)+ drivers 四函数契约 + manifest(锁能力边界:底模血统/训练分布/工具 schema/pass 记录)+ 使用流程 CLI(lf.wrap/record/compile/verify/serve)。
关键设计:**manifest 是"不可拆"的解药**——把可拆部分显式钉进产物,重编译问题可管理。

## 第 13 轮:能辅助 LLM 自主进化吗

**查证**:Absolute Zero(arXiv:2505.03335,清华,自出题自解题,代码执行器当裁判,零外部数据 SOTA)+ Darwin Gödel Machine(arXiv:2505.22954,Sakana,自改代码的 agent,SWE-bench 自我提升)。

**结论**:框架已有三环(数据环=tracer/transitions、权重环=RFT+RL、记忆环=经验固化),缺两模块(**任务发生器**、**外部锚**);三堵墙:**验证器天花板**(自进化上限=验证器上限)、**分布坍缩**(Nature 2024 model collapse,纯自产数据退化)、**自指安全**(goal drift);定案:**带外部锚的自动改进循环**,协同进化 = 与真实环境协同,不是闭门自训。

## 第 14 轮:外部测评设计

**用户想法**:部署两个这样的 LLM agent,观测训练前 vs 训练后;但最终上线哪个测评集,没想好如何突破。

**结论**:双 agent 影子对比 ≠ 测评集,只是第三层。三层金字塔:**金标集(冻结,上线门)/ 可验证自动评测(快速门)/ 双 agent 影子(现实门)**。金标集是生产线:真实失败案例做种子 → 分层抽样 → LLM-as-judge 人工锚定 → 版本化+换血+污染检测+canary 私有切片。上线门判据:全切片无回归+污染阈值+canary+影子期业务指标。**结果账本**(30 天真实回流)= 下一轮金标原料 + 训练真实奖励——协同进化里"环境"的具体形态。

## 第 15 轮:最终载体是机器人

**查证**:Figure Helix——S2(7B VLM,慢,~7-9Hz,输出语义隐向量)+ S1(轻量视觉运动策略,200Hz),S1 以 S2 隐向量为条件;行业已收敛到双系统 + 隐向量交接。

**结论**:机器人上前面所有"可选"变"必选"(控制回路频率下文字根本跟不上);Helix 的隐向量交接 = 用户触发层雏形。三个改写:①验证器反而简单(物理世界=裁判,结果账本=任务成败台账),新风险变 sim-to-real gap;②安全层升级为**硬实时、非学习、低于 S1、独立于一切学习组件**(工业安全控制器规范);③双机对账评测天然成立。安全红线从"审计偏好"变"物理安全要求"。

## 第 16 轮:建仓(工程开始)

**执行**:创建 `D:\Project\llmagnet`,骨架(forge 五件套/rt 四件套/drivers/manifest/README)+ 五个参考组件浅克隆到 refs/(agent-lightning/LatentMAS/coconut/Mage/mem0,407MB)。

## 第 17 轮:MVP 方案 v1(小模型+自研 agent)

**结论**:不验证框架完整性,验证四个假设(H1 隐循环/H2 触发探针/H3 fork 回注/H4 RFT+GRPO);硬件分档 A/B/C;任务集 = 350 条程序可判分小任务;每阶段产出"可写进报告的数字"。

## 第 18 轮:MVP 方案 v2(按实租云机重写)

**输入**:AutoDL 实例,RTX 3090 24GB / 14vCPU / 60GB 内存 / 系统盘 30GB + 数据盘 50GB / torch 2.8 + Py3.12 + CUDA 12.8 预装 / ¥1.56 时。
**要点**:数据盘钉 HF_HOME 与 checkpoint;hf-mirror 加速;torch 勿动;refs/coconut 只当配方;模型 = Qwen2.5-1.5B 主力 + 0.6B GRPO;四阶段工时与花费明细;加卡时机 = Phase 4(生成/训练分离 = Agent Lightning 解耦最小实物)。

## 第 19 轮:本机写好 + Runbook 模式(执行中)

**用户要求**:能在本机做的都在本机写好,数据集/模型下载/执行步骤写成部署式 Runbook,到机器直接照跑;预算可翻倍(后明确 ≤¥6000)。

## 第 20 轮:agent 改用 dsh(架构切换)

**用户要求**:agent 用 dsh(一切皆插件)的,以后换任务好弄。

**探索结论**(对本地 D:\Project\dsh 源码):
- 插件 = TS/JS ESM 模块,`apply(ctx)` + `inject:['tools']` + `ctx.tools.register(defineTool({...}))`,cordis.yml + patch 加载;
- LLM:`llm-pi-ai` 自定义 route(api: openai-completions + baseURL)→ 指向 vLLM;
- 无头三路:CLI `dsh --profile headless` / TS SDK / **Python SDK(deepseek-harness-sdk,自带捆绑 runtime,无需 Node)**;
- 插件必须 JS/TS,不能 Python;Python 工具可包成 MCP server。

**落地代码**:judge.py(判分)/ dsh-plugin(src/mvp-tools.js:calculator+kb_query;cordis.yml 组合)/ runner_dsh.py(批量驱动+统计)/ requirements.txt / RUNBOOK.md(八步部署手册+排障表)。
任务生成器迭代三版:去重截断问题 → 扩知识库(40 商品/24 券/400 订单)→ 补抽逻辑+金标排除;最终 300/50/5 全达标,**107 条订单类两跳任务独立验算全过**。

## 第 21 轮:交接包

**用户想法**:云机装 ZCode headless,拉下来继续跑。

**结论**:会话跨机续接不可保证,但真正要带走的是仓库+上下文。新增 **AGENTS.md**(冷启动上下文:状态/四假设/红线/架构事实/约定);打包 llmagnet-transfer.tar.gz(38KB,refs 不入包,Phase 1 重克隆)。

## 第 22 轮:PRD + 对话导出 + git(本文件)

**用户要求**:把 PRD 写详细(前因后果/用户决策),整个对话导出成 md,整个项目进 git,云机 git 拉取开炮,起点尽量规划好。

**落地**:docs/PRD.md(本文档姊妹篇:PRD)+ docs/CONVERSATION_LOG.md(本文件)+ git 仓库化 + push 指引。

---

## 本纪要未含的实时链接速查

- 跑分与格局:mem0.ai/blog/state-of-ai-agent-memory-2026 · letta.com/blog/benchmarking-ai-agent-memory · blog.getzep.com/lies-damn-lies-statistics
- 论文:arxiv.org/abs/2310.08560(MemGPT)· /abs/2504.19413(Mem0)· /abs/2501.13956(Zep)· /abs/2507.03724(MemOS)· /abs/2507.07957(MIRIX)· /abs/2501.00663(Titans)· /abs/2412.09764(Memory Layers)· /abs/2402.04624(MemoryLLM)· /abs/2502.00592(M+)· /abs/2504.19413 · /abs/2605.14038(工具意图探针)· /abs/2511.09149(Interlat)· /abs/2511.20639(LatentMAS)· /abs/2602.16943(工具调用安全)· /abs/2607.03333(SPORK)· /abs/2607.24904(Mage-VL)· /abs/2505.03335(Absolute Zero)· /abs/2505.22954(DGM)· /abs/2508.03680(Agent Lightning)
- 压缩回注:arxiv.org/abs/2307.06945(ICAE)· /abs/2304.08467(Gist)· /abs/2406.06110(RCC)
- Anthropic:anthropic.com/research/global-workspace · Fable 5 & Mythos 5 系统卡 PDF
- 机器人:figure.ai/news/helix
- 综述:github.com/Shichun-Liu/Agent-Memory-Paper-List · arxiv.org/abs/2507.21046(自进化 agent)· nature.com/articles/s41586-024-07566-y(model collapse)
