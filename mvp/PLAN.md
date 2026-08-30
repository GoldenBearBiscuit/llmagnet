# LLMagnet 个人级 MVP 方案(v2,按实租算力机定制)

> 硬件:AutoDL 式实例,RTX 3090 24GB ×1 / 14 vCPU / 60GB 内存 / 系统盘 30GB + 数据盘 50GB,
> PyTorch 2.8.0 + Python 3.12 + CUDA 12.8(已预装),¥1.56/时按量计费。
> 一句话:Qwen2.5-1.5B + 自研 agent,在四个阶段里逐个验证大架构的四个核心假设。
> GPU 可加:Phase 4 需要提速时加第二张卡,顺便把 Agent Lightning 的解耦范式真跑起来。

## 0. 明确砍掉什么(不做)

- ❌ Mage-VL 视频感知 / 机器人 / 多 agent 协作(留 v1.x)
- ❌ 完整 Agent Lightning 框架接入(个人规模用 TRL;第二张卡到位后再上它的 Server/Client 形态)
- ❌ LangChain 等框架(全自研纯 Python)

## 1. 四个假设(主线不变)

| # | 假设 | 来源 | 验收标准 |
|---|---|---|---|
| H1 | 明文 CoT → 隐空间循环,质量不降、token 大降 | Coconut / LatentMAS | 质量掉幅 ≤2%,token 成本降 ≥30% |
| H2 | "要不要调工具"在隐状态里线性可读 | arXiv:2605.14038 | 探针 F1 ≥ 0.8 |
| H3 | 工具结果编码回隐状态,质量保持 | ICAE / fork 设计 | 回注后成功率 ≥ 明文注入的 95% |
| H4 | 可验证奖励 RFT/GRPO,小模型越调越准 | Absolute Zero / RLVR | 3 轮迭代成功率单调升 |

任何一个被证伪都是有效结果,写进 reports/ 并回头修订大架构。

## 2. 这台机器的实战要点(踩坑前置)

```bash
# ① 磁盘:系统盘只有 30GB,模型/数据集/checkpoint 全部放数据盘
export HF_HOME=/root/autodl-tmp/hf
export DATA=/root/autodl-tmp/llmagnet
# ② 网络:走 HF 镜像,别直连
export HF_ENDPOINT=https://hf-mirror.com
# ③ torch 2.8 已预装好——不要重装,只装周边(选与 torch2.8/py3.12 兼容的版本)
pip install transformers peft trl datasets accelerate
# ④ 监控:6006 端口开 TensorBoard,训练时盯 loss/reward
tensorboard --logdir $DATA/runs --port 6006
```

- **按量计费纪律**:每个阶段结束→确认 checkpoint 已存数据盘→可关机(AutoDL 关机只收磁盘费);长训练挂 nohup/tmux,断线续跑。
- **磁盘预算**:Qwen2.5-1.5B 权重 ~3GB,3B ~6GB,LoRA 适配器每个 ~100MB,合并模型 ~3GB/个,数据集 <1GB——50GB 够用,但合并版模型留 2 个最新即可,旧的删。
- **refs/coconut 是 2024 年老代码**,依赖旧版 transformers:只当**配方参考**(它怎么把 CoT 换成连续思维、怎么截断梯度),代码自己重写,别硬装它的环境。

## 3. 模型选型

| 用途 | 模型 | 理由 |
|---|---|---|
| 主力 | **Qwen2.5-1.5B-Instruct** | 24GB 上 LoRA 从容;中英双语;JSON 工具调用听得懂 |
| Phase 4 GRPO 专用 | Qwen2.5-0.6B-Instruct | GRPO 每步要生成 N 条候选,0.6B 让单卡 3090 舒服跑完 |
| 冲一冲(可选) | Qwen2.5-3B-Instruct | 基线太弱时升级;LoRA SFT 没问题,GRPO 会紧张 |

### 3.5 agent 架构:dsh(用户指定,"一切皆插件")

```
训练/评测侧(Python):transformers + peft + trl + datasets(torch 2.8 预装勿动)
agent 侧:dsh(DeepSeek Harness)
  - 工具 = dsh 插件(mvp/dsh-plugin,JS defineTool 注册 calculator/kb_query)
    → 换任务 = 换插件或换 kb.json,评测驱动零改动
  - 模型端点:vLLM 起 Qwen 的 OpenAI 兼容服务,dsh 经 llm-pi-ai 自定义 route 指向
  - 驱动:deepseek-harness-sdk(Python 驱动捆绑 runtime,机器无需装 Node)
评测驱动:mvp/harness/runner_dsh.py(逐任务 run → judge 判分 → traces/metrics)
```

## 4. 任务集(可验证奖励的来源)

自建 350 个多步小任务,**全部程序判分**,三类:

- **算术组合**(120):calculator 工具算多步账单——买 N 件 × 单价,叠折扣券,算总价
- **查表推理**(120):本地 JSON 库查(商品价/课程时间/城市距离),再组合计算
- **两跳问答**(110):先查 A,用 A 的结果查 B(强制多步,给触发层制造决策点)

每条:instruction + tools 白名单 + 标准答案 + 判分函数(数值容差/精确匹配)。
切分:`train_300.jsonl` + `golden_50.jsonl`(**封存**,训练侧不可见——红线 #2)。

## 5. 四个阶段(含 3090 实测工时与花费)

### Phase 0:基线 harness(~4h GPU,≈¥6,1-2 天)

1. 本机已完成:任务生成器(kb+300 训练+50 金标+5 冒烟,种子固定,两跳答案已全量独立验算)
2. 云机按 RUNBOOK.md 执行:起 vLLM(Qwen1.5B OpenAI 兼容端点)→ dsh 插件挂工具 → 冒烟 5 条
3. 跑 300 任务基线:成功率 / 分 tag 指标 / 平均时延;失败案例分桶(工具没调/参数错/推理错)
4. 全部走 dsh:agent 循环、工具执行在 dsh 侧;runner_dsh.py 只管驱动/判分/统计

### Phase 1:H1 隐循环(~15h GPU,≈¥23,1 周)

1. RFT 前半:基线 agent 跑训练集,留答对轨迹(~3h)→ 蒸馏数据
2. Coconut 式 LoRA 蒸馏(重写版配方):CoT 前 k 步换成连续思维(末隐状态喂回 embedding),
   k=2 起步;r=16,seq 2048,bf16(~6-8h)
3. 三组对比:明文 CoT / LatentMAS 式零训练隐循环(便宜,先试)/ 蒸馏隐循环
4. **产出 H1 判定**:golden_50 上 质量/延迟/token 三元组

### Phase 2:H2 触发层探针(~1h GPU,≈¥2,2-3 天)

1. 从 Phase 0 traces 抽"决策点隐状态",标注"下一步是否调工具"
2. 线性探针(逻辑回归,CPU 都行)→ F1;接进循环做 silent/call/speak 门控
3. **产出 H2 判定**:F1 + 门控版省了多少次模型调用

### Phase 3:H3 fork 回注(~6h GPU,≈¥10,3-4 天)

1. 工具结果(200 字查表 JSON)三注法:明文回塞(基线)/ 自身 encoder 做 soft prefix
   (零训练)/ ICAE 式小压缩器(LoRA,~4h)
2. **产出 H3 判定**:回注成功率 / 明文基线,上下文 token 省多少

### Phase 4:H4 迷你自进化(~35h GPU,≈¥55,1-2 周)

1. RFT 闭环(主力,稳):跑任务 → 留对的 → SFT(~2h/轮)→ 再跑,3 轮看曲线
2. GRPO(进阶,0.6B):TRL GRPOTrainer,8 候选/步,奖励 = 答对 +1、
   工具格式错 -0.5(迷你 AIR:工具状态当中间奖励);单卡 ~20h 出曲线
3. **产出 H4 判定**:3 轮成功率曲线 + reward hacking 检查(是否只挑简单题)

### 加卡时机(你说的"GPU 可以加")

Phase 4 想提速/上 1.5B GRPO 时,加第二张卡:一张跑 **vLLM 候选生成服务**,
一张跑训练——这就是 Agent Lightning "Server/Client 解耦"的最小实物版,
把 mvp 的 Phase 4 和大框架 Forge 的 trainer 接口对上。

## 6. 预算(上限 ¥6000,由用户 2026-08-30 定)

核心 MVP 依旧百元级;多出来的预算**不买结论,买实验矩阵的宽度**:

| 档 | 内容 | 预估 |
|---|---|---|
| 核心 | Phase 0-4 按 §5 原样执行 | ~¥150 |
| EXP-A | 3B 模型对照基线(1.5B 结论是否随规模成立) | ~¥40 |
| EXP-B | 第二张卡:vLLM 生成与训练分离,1.5B 全速 GRPO(Agent Lightning 解耦最小实物) | ~¥250 |
| EXP-C | 任务集扩到 2000 条 + RFT 加到 5 轮(看进化曲线拐点) | ~¥200 |
| EXP-D | GRPO 超参/奖励设计扫描(4-6 个配置,含 reward hacking 对照组) | ~¥500 |
| EXP-E | Phase 1 隐循环 k=2/4/8 步长扫描 + 3B 蒸馏 | ~¥300 |
| 全开 | 上述全部 | ~¥1500 |

¥6000 上限 ≈ 全开之后还能支撑 3-4 轮返工/加赛;**先跑核心,再按结果挑 EXP**。

## 7. 风险表(比 v1 少了一条:没有 Windows 坑了)

| 风险 | 概率 | 对策 |
|---|---|---|
| 零训练隐循环在 1.5B 上不可用 | 高 | 换 Coconut 蒸馏;都败则记录负结果(H1 修订) |
| 1.5B 基线成功率太低 | 中 | 任务难度下调 / 升 3B(SFT 没问题,GRPO 留 0.6B) |
| GRPO 单卡不稳/太慢 | 中 | 退回纯 RFT,H4 依然可验证;或加第二张卡 |
| 数据盘塞满 | 低 | 合并模型只留最近 2 个;LoRA 适配器很小 |
| 四个假设全败 | 低 | 按负结果重设计大架构——这钱花得值 |

## 8. 产出物与目录

```
mvp/
├── PLAN.md            本文档
├── RUNBOOK.md         云机部署执行手册(照步骤跑,含排障表)
├── requirements.txt   云机 pip 依赖(torch 预装勿动)
├── dsh-plugin/        dsh 工具插件(JS)+ cordis.yml 组合
├── harness/           评测驱动:runner_dsh.py(Python SDK 驱动 dsh)+ judge.py
├── tasks/             generate_data.py + kb.json + train_300 + golden_50(封存)+ smoke_5
├── phase1_latent/     H1:LatentMAS 式试跑 + Coconut 蒸馏(重写版)
├── phase2_gate/       H2:探针 + 门控接入
├── phase3_fork/       H3:三种回注对比
├── phase4_rft_rl/     H4:RFT / GRPO 循环
└── reports/           每阶段一页:假设 → 数字 → 结论(成立/证伪/存疑)
```

每个阶段的代码同时就是大框架 Forge 部件的原型:
harness→forge/tracer、Phase1→forge/distill、Phase2→rt/gate、Phase3→rt/fork_exec、
Phase4→forge/trainer。MVP 跑通之日,Forge 接口设计自动落地。
