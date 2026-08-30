"""fork 执行器:工具/动作的唯一落地边界,同时是审计日志边界。

设计对应(红线 #3):明文只允许出现在这里——
  出向:触发层的工具意图 → 薄解码头序列化成参数(明文),执行工具/动作;
  回向:结果明文 → 编码回隐状态 → 注回主循环(三种方案按保真度选):
      A 直接 encode(零训练,LATentMAS 式)   B 压缩器(ICAE/RCC,LoRA 训练)
      C 侧分支自持明文 KV + cross-attention / 写入神经记忆
多模态结果(截图/音频/力觉)直接过对应编码器进 latent,跳过文字化。

机器人语境:工具 = 技能原语(抓取/导航/开门);出向终点是动作头
(RT-2/OpenVLA/π0 先例),回向终点是力觉/视觉观测的隐编码。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ForkLog:
    """明文审计日志:fork 边界天然留痕,注入前可做内容过滤。"""
    tool: str
    params_text: str            # 出向明文(唯一落地点)
    result_text: str | None     # 回向明文(编码前)
    inject_mode: str            # A_encode / B_compress / C_kv
    blocked: bool = False       # 内容过滤拦截标记
    extra: dict[str, Any] = field(default_factory=dict)


class ForkExecutor:
    def __init__(self, tools: dict[str, Callable], encoder: Any = None,
                 filter_fn: Callable[[str], bool] | None = None):
        self.tools = tools
        self.encoder = encoder            # 结果 → 隐状态的编码器(-O2 训练产物)
        self.filter_fn = filter_fn        # 注入前内容过滤(embedding 注入更隐蔽,必须过滤)
        self.logs: list[ForkLog] = []

    def execute(self, tool: str, params_text: str) -> Any:
        """执行并返回"注回主循环的隐状态"(不是明文结果)。"""
        raise NotImplementedError(
            "MVP:encoder 用目标 LLM 自身 encoder 模式取隐状态(方案 A,零训练);"
            "升级:ICAE/RCC 压缩器(方案 B,见 forge/fork)"
        )
