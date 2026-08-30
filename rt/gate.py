"""三合一触发层(本框架的核心创新点)。

一个可学习门,同时负责三件事——现有工作各占一角,无人合并:
  1. intent   : 工具意图门。"需要工具"信号在隐状态中线性可读
                (arXiv:2605.14038),在生成任何工具调用 token 之前即可读出。
  2. memory   : 记忆读回兼唤醒信号。记忆层的 read-out 就是隐空间的
                门控输入(Titans surprise 门控 + 记忆即注意力门控)。
  3. halt     : 停止判定。PonderNet/ACT 式可学停顿,决定"拿到答案了没"。

训练:与 halt 策略在 forge/trainer 里联合训练;推理时逐时间戳评估,
决定 沉默(silent) / 开口(speak) / 调工具(call) 三分支。
机器人语境:即 Helix 的 S2→S1 交接门控的推广(固定交接 → 可学习门)。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class GateAction(Enum):
    SILENT = "silent"      # 继续隐循环/继续观察
    SPEAK = "speak"        # 停止门放行 → 最终答案落地为文字
    CALL = "call"          # 工具意图门放行 → 进 fork


@dataclass
class GateDecision:
    action: GateAction
    confidence: float
    surprise: float        # 记忆写入门控信号(高 surprise → 回写长期记忆)


class TriggerGate:
    """所有判定从隐状态读出,不从明文读出(设计红线:主循环不落地)。"""

    def __init__(self, intent_head: Any = None, halt_head: Any = None,
                 memory_iface: Any = None, surprise_threshold: float = 0.7):
        self.intent_head = intent_head
        self.halt_head = halt_head
        self.memory_iface = memory_iface
        self.surprise_threshold = surprise_threshold

    def evaluate(self, hidden: Any, state: Any) -> GateDecision:
        raise NotImplementedError(
            "MVP:intent_head 用 arXiv:2605.14038 的线性探针冷启动;"
            "halt_head 用 PonderNet 式期望损失训练"
        )

    def should_write_memory(self, surprise: float) -> bool:
        return surprise >= self.surprise_threshold
