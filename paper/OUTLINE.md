# 论文规划(OUTLINE)

> 对应实验:mvp/ 四阶段。写作原则:**每完成一个 Phase,reports/ 里的一页报告直接变成论文一节的素材**——论文不是写出来的,是实验矩阵自动长出来的。

## 1. 这篇论文能不能发?(诚实评估)

| 目标档次 | 可行性 | 需要补什么 |
|---|---|---|
| arXiv 预印本 | ✅ 现在的设计就够 | 无 |
| 国际 **workshop**(NeurIPS/ICML agent 方向 workshop、LLM Agents @ 顶会) | ✅ 最匹配 | H1-H4 完整跑通 + 消融 |
| 中文期刊/学报(小论文,如计算机工程与应用/计算机科学档) | ✅ | 加中文写作 + 补国内相关工作的对比表 |
| 主会(ACL/EMNLP/NeurIPS 主track) | ❌ 现在不行 | 需要官方基线复现(Coconut/ICAE 原代码)、多规模(1.5B/3B/7B)、标准基准(LoCoMo/GSM8K 级),即 PLAN 里的 EXP 菜单全开 |

**卖点(贡献声明,按强度排序)**:
1. **三合一触发层**:工具意图 + 记忆读回 + 停止判定 合并为一个可学习门控——文献里三者各占一角,无人合并(H2 是它的直接证据);
2. **工具 I/O 回注(fork)的保真/成本 tradeoff 实证**:明文/直接 encode/压缩器三档系统对比(H3);
3. **小模型(≤1.5B)上隐空间 agent 的可行性实证,含负结果**:哪条路线在小规模上不成立(H1 可能部分证伪——这在 workshop 是有价值的发现);
4. 若 H4 成立:可验证奖励下小 agent 的自改进曲线(H4)。

## 2. 题目候选

- 中性实证风:**"Toward Latent-Space Agents: Latent Reasoning, Tool-Intent Gating, and Tool-Output Re-Encoding in Small Language Models"**
- 系统命名风:**"LLMagnet: Compiling Tool-Using Agents out of Plaintext"**
- 中文版:**《隐空间智能体:小语言模型上不落地的推理与工具调用实证研究》**

## 3. 章节结构(逐节映射到实验产物)

| 章节 | 内容 | 素材来源 |
|---|---|---|
| 1 Introduction | 文字 token 是低带宽接口:agent 循环的 token 花在明文 CoT + 工具 I/O 重复上;我们提出四件套并逐件验证 | PLAN §1 四假设 |
| 2 Related Work | 潜空间推理(Coconut/LatentMAS);记忆(MemGPT/Mem0/Zep);上下文压缩(ICAE/Gist/RCC);工具意图探针;RL(Agent Lightning/Absolute Zero);双系统机器人(Helix) | refs/ + docs/CONVERSATION_LOG.md 速查表 |
| 3 Method | 形式化:隐循环为 POMDP 段;三合一门 G(τ)=intent×memory×halt;fork 回注三档定义;manifest 能力边界 | forge/rt 骨架 docstring |
| 4 Experiments | 4.1 基线与任务集;4.2 H1 三组对比;4.3 H2 探针+门控;4.4 H3 三档回注;4.5 H4 RFT/GRPO 曲线 | mvp/reports/phase0-4 |
| 5 Analysis | 失败分桶;reward hacking 观察;小规模 vs 文献规模的落差讨论(诚实) | traces + 失败案例 |
| 6 Limitations & Conclusion | 单卡小规模;自定义任务集;安全/审计边界(manifest 红线) | PRD §8 |

## 4. 图表清单(实验做完图表自动有)

| 编号 | 内容 | 数据来自 |
|---|---|---|
| Fig.1 | 架构总图(感知→门→隐循环→fork→文字) | README 图重绘 |
| Fig.2 | H1:质量-延迟-Pareto(明文 CoT vs 零训练隐循环 vs 蒸馏隐循环) | phase1 results |
| Fig.3 | H2:决策点隐状态线性探针 F1(分层)+ 门控版 token 节省 | phase2 |
| Tab.1 | H3:三种回注方式 成功率/token/延迟 对照 | phase3 |
| Fig.4 | H4:RFT/GRPO 迭代成功率曲线 | phase4 |
| Tab.2 | 相关工作对照表:谁覆盖了触发/记忆/停止的哪一角(我们合并了三者的论证) | CONVERSATION_LOG 第4/6轮 |

## 5. 投稿与时间线建议

- Phase 0-2 完成 → 先挂 **arXiv**(占坑,中文小论文同时可写)
- Phase 3-4 完成 + EXP 消融 → 投最近的 **agent 方向 workshop**(看当时 CFP;NeurIPS/ICML/ACL 都有常设 agent workshop)
- 中文版可与英文版共享图表,投学报/科技核心档
- 写作节奏:**每 Phase 报告日 = 论文素材日**,不要攒到最后

## 6. 写作纪律(来自本项目踩过的坑)

1. 所有自报数字必须有 golden_50(封存集)支撑,写明"未参与任何调参"——对应 PRD 红线 2;
2. 跑分大战的教训(第 1-2 轮调研):不自称 SOTA,只做受控对比,声明任务集是自定义的;
3. 负结果如实写(H1 若在小模型上不成立,这本身是论文的记忆点);
4. 引用格式统一用 `references.bib`(已配好,arXiv ID 均经核实)。
