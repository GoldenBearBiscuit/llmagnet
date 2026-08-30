"""隐空间循环驱动器(-O1 起生效)。

设计对应:Coconut 式连续思维 / LatentMAS 式零训练隐循环。
推理在最后一层隐状态上自回归迭代,全程不解码成文字;
只有 halt 门放行时,才把最终隐状态一次性映射成文本。

与 TextAgent 的关键差异:循环体不产生 token,credit assignment
发生在隐轨迹层面(见 forge/trainer)。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol


class LatentPolicy(Protocol):
    """编译产物暴露的最小接口:可被 -O1(零训练)或 -O3(RL 训后)实现。"""

    def step(self, hidden: Any, obs: Any) -> tuple[Any, float]:
        """隐空间单步:输入当前隐状态与观测,返回(新隐状态, halt 信号 logit)。"""
        ...

    def decode(self, hidden: Any) -> str:
        """最后一步:隐状态 → 文本(整个循环唯一的一次文本生成)。"""
        ...


@dataclass
class LatentLoopResult:
    answer: str                 # 最终答案(全程唯一落地的文本)
    steps: int                  # 隐循环步数(审计用)
    halt_logit_trace: list[float] = field(default_factory=list)
    hidden: Any = None          # 末隐状态(fork 回注的注入点)


def run_latent_loop(
    policy: LatentPolicy,
    obs: Any,
    max_steps: int = 64,
    halt_threshold: float = 0.5,
    on_step: Callable[[int, float], None] | None = None,
) -> LatentLoopResult:
    """驱动隐循环直到停止门放行或步数耗尽(红线:不产生中间明文)。"""
    raise NotImplementedError("MVP:用 LatentMAS 的 last-layer 隐状态循环实现")
