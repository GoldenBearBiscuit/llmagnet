"""-O2:工具 I/O 编译。

出向:触发层工具意图 → 参数解码头(训练一个从隐状态解码结构化
      调用的头;机器人语境 = 动作头,RT-2/OpenVLA/π0 先例);
回向:结果明文 → 压缩回注,三档按保真度/成本选:
      A 直接 encode(零训练)   B 压缩器:ICAE(arXiv:2307.06945)/
      RCC(arXiv:2406.06110)/ Gist(arXiv:2304.08467),LoRA 只训压缩器
      C 侧分支自持明文 KV + cross-attention
训练数据来自 tracer 采集的 fork 边界对(明文 ↔ 实际用到的信息)。
"""

from __future__ import annotations


def train_result_compressor(pairs_path: str, base_model: str, mode: str = "B") -> str:
    """fork 边界 (结果明文, 实际使用信息) 对 → 压缩回注编码器 checkpoint。"""
    raise NotImplementedError


def train_action_head(traces_path: str, base_model: str) -> str:
    """隐状态 → 结构化工具调用/动作 的解码头(机器人 = 动作头)。"""
    raise NotImplementedError
