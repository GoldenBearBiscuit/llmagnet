# LLMagnet — 可编译、可进化的隐空间 Agent 框架

> 定位:输入「开源权重 LLM + 现成 agent」,输出「隐空间 agent」的编译器套件 + 薄运行时。
> 目标场景:实时多模态(视频流/机器人)+ 高并发长链路生产任务;终局形态是带外部锚的自进化闭环。

## 总体架构

```
输入:开源权重 LLM + 现成 agent(工具定义 + 任务集 + 奖励函数)
  -O0  原样输出(文本 agent,基线)
  -O1  CoT 蒸馏:文本思维链 → 隐空间循环(Coconut 式)
  -O2  工具 I/O 编译:调用点 fork + 结果编码回注(ICAE/RCC 式)
  -O3  端到端 RL:触发门/停止/记忆读写进权重(Agent Lightning 范式 + AIR)
输出:agent.compiled.pt + manifest.yaml + 薄运行时
```

运行时数据流(全程对主循环"不落地"):

```
感知(Mage-VL 码流原生)
   ↓
触发层 = 工具意图 + 记忆读回 + 停止判定(三合一门)
   ↓
隐空间推理循环(最后一步才映射成文字)
   ↓ ↘ 高 surprise 内容回写记忆
fork ──→ 参数序列化成明文(唯一落地处,留日志)──→ 执行工具/动作
   ↑ ←── 结果明文 → 编码回隐状态 → 注回主循环
```

## 目录结构

```
forge/          构建时(重,GPU 集群)
  tracer/       三类钩子:LLM 调用点 / 工具边界 / 任务边界
  distill/      -O1 Coconut 式 CoT→隐思维蒸馏
  fork/         -O2 工具参数解码头 + 结果压缩回注(ICAE/RCC)
  trainer/      -O3 解耦 RL(Server/Client、transitions、AIR、halt 策略)
  verify/       验收:切片级回归 + 污染检测 + canary,对 -O0 基线
rt/             运行时(极薄)
  loop.py       隐空间循环驱动器
  gate.py       三合一触发层
  fork_exec.py  工具/动作执行 + 明文审计边界
  memory/       外置记忆接口(可插拔)
drivers/        框架驱动(4 函数契约:list_tools / emit_tool_call / report_reward / stream_trace)
out/            编译产物(agent.compiled.pt + manifest.yaml + probes/)
refs/           参考组件(浅克隆的开源依赖,见下)
```

## refs/ 里的组件与用途

| 仓库 | 用在哪 |
|---|---|
| `refs/agent-lightning` (MSR) | -O3 训练范式:解耦 Server/Client、轨迹→transitions、AIR 中间奖励 |
| `refs/LatentMAS` | -O1 的零训练起点:last-layer 隐状态直接当输入的隐循环 |
| `refs/coconut` (Meta) | -O1 蒸馏:明文 CoT → 连续思维的训练配方 |
| `refs/Mage` (MSR) | 实时感知前端:Mage-VL 码流原生视觉编码器 |
| `refs/mem0` | 外置记忆参考实现(抽取/更新管道) |

## 设计红线(来自架构论证,不可违背)

1. **guardrails/急停/安全层永不编译进隐空间**——机器人场景下是物理安全要求,层级独立于一切学习组件。
2. **外部锚不可自改**——冻结评测集与奖励函数的修改权在人类;agent 只能优化,不能动尺子。
3. **明文只允许出现在 fork 边界与最终答案**——fork 边界同时是审计日志边界。
4. **自进化数据环必须持续注入真实流量/物理反馈**——纯自产数据会分布坍缩。
5. **manifest 锁能力边界**——底模血统、训练分布、工具 schema 版本、编译 pass 记录;越界行为无保证。

## 里程碑

- [ ] MVP:tracer + verify + -O1(LatentMAS 零训练隐循环),同任务集验证延迟收益
- [ ] v0.1:-O2 fork 落地,工具 I/O 不落地,token 成本曲线成立
- [ ] v1.0:-O3 RL + manifest + 探针审计,完整"输入 agent → 输出编译产物"闭环
- [ ] v1.x:机器人落地(sim 任务库回归门 + 真机双机对账 + 硬安全层集成)
