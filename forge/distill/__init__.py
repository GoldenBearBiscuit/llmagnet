"""-O1:明文 CoT → 隐空间循环 蒸馏(Coconut 式)。

两条实现路线:
  零训练:refs/LatentMAS —— last-layer 隐状态直接当输入循环使用(MVP 起点);
  训练:  refs/coconut —— 把 traces 里的明文 CoT 重放编码成连续思维,
          教 halt/触发门在隐轨迹上做 credit assignment。
产出:rt/loop.LatentPolicy 的可运行 checkpoint。
验收(verify):同任务集上 对 -O0 质量、延迟、token 成本 三项。
"""

from __future__ import annotations


def distill_from_traces(traces_path: str, base_model: str) -> str:
    """读 traces.jsonl,蒸馏出隐空间循环策略;返回 checkpoint 路径。"""
    raise NotImplementedError
