"""三类钩子:LLM 调用点 / 工具边界 / 任务边界(Agent Lightning 式,agent 无关)。

挂钩即记录,不改 agent 逻辑:
  - LLM 调用点  → 每次调用 = 一个 transition(输入, 输出, 奖励)
  - 工具边界    → fork 出入明文 + 工具状态(AIR 中间奖励原料)
  - 任务边界    → 任务终局奖励 + 成败台账(机器人语境 = 结果账本)
轨迹采集走 OpenTelemetry;产出 traces.jsonl 供 forge/trainer。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Transition:
    input_t: Any        # 本次 LLM 调用的输入(-O1 后 = 隐状态观测)
    output_t: Any       # 本次调用的输出(文本或隐轨迹段)
    reward_t: float | None   # 任务终局回填;中间奖励由 AIR 填
    tool_status: str | None = None  # 工具调用状态 → AIR 原料


@dataclass
class TraceRecorder:
    transitions: list[Transition] = field(default_factory=list)

    def wrap_llm(self, llm_call: Callable) -> Callable:
        """包装 LLM 调用点(第 0 档接入方式:框架零改动)。"""
        raise NotImplementedError

    def wrap_tool(self, tool_call: Callable) -> Callable:
        """包装工具边界(同时是 rt/fork_exec 的审计日志来源)。"""
        raise NotImplementedError

    def report_reward(self, task_id: str, reward: float) -> None:
        """任务边界:终局奖励回填到该任务的所有 transitions。"""
        raise NotImplementedError
