"""验收:上线门(每一级编译 pass 的回归测试)。

三层评测金字塔(机器人版):
  第 1 层 金标集(冻结)    → 回归门:切片级无回归 + 污染检测 + canary 私有切片
  第 2 层 可验证自动评测    → 快速门:执行器/仿真可核对的任务,高频反馈
  第 3 层 双 agent 影子对比 → 现实门:训练前后双机并行跑同一任务队列对账
结果账本(任务成败台账)回流 = 下一轮金标集换血 + 训练真实奖励。
红线 #2:本模块和金标集对训练侧只读,agent 永远改不了尺子。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GateReport:
    passed: bool
    slice_regressions: list[str]   # 任一切片掉点超阈值 → 拦(不是只看均分)
    contamination_ratio: float     # 训练数据与金标集重叠率
    canary_passed: bool | None
    metrics: dict                  # quality / latency / cost,对 -O0 基线


def verify_gate(candidate: str, baseline_o0: str, golden_set: str,
                contamination_threshold: float = 0.02) -> GateReport:
    raise NotImplementedError
