"""-O3:端到端 RL(范式来自 refs/agent-lightning,优化对象换成隐轨迹)。

架构:Lightning Server(训练控制器,OpenAI 兼容端点供新权重)
     + Lightning Client(agent 运行时,采轨迹,无需 GPU 共置)。
数据:transitions(输入, 输出, 奖励);每次 LLM 调用/隐循环段 = 一个 transition。
算法:token 级复用 PPO / GRPO / REINFORCE++;层级 credit assignment
     (当前朴素法:episode 内均分最终回报;学习型 value function 是升级项)。
AIR:Automatic Intermediate Rewarding——工具状态/压缩保真度/任务子目标
     自动折成中间奖励,对抗稀疏奖励(机器人语境:子任务成功信号)。
自进化扩展(终局):任务发生器(自出题,Absolute Zero 式)+ 真实流量注入
     (红线 #4:自产数据占比上限见 manifest)+ 外部锚不可自改(红线 #2)。
机器人语境:白天干活采 episodes,云端夜里训练,早晨带 manifest 下发。
"""

from __future__ import annotations

from typing import Any


class LightningServer:
    """训练控制器:批量派发任务、事件驱动训练循环、供当前权重。"""

    def __init__(self, base_checkpoint: str, reward_fn: str, air_signals: list[str] | None = None):
        raise NotImplementedError


class LightningClient:
    """agent 运行时侧:执行任务、回报 transitions;不持有训练逻辑。"""

    def __init__(self, server_endpoint: str, driver: Any = None) -> None:
        raise NotImplementedError
