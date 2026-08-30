"""外置记忆接口(可插拔)。

设计对应:记忆 stays 外置(可拆、可审计、可回滚)——红线之外的可拆部分。
参考实现 refs/mem0(抽取/ADD/UPDATE/DELETE/NOOP 管道);
进阶:高 surprise 内容经 forge/trainer 固化为参数化记忆(经验→权重,
自进化 agent 综述 2507.21046 指出的前沿方向)。

机器人语境:技能库(Voyager 式)+ 经验台账;成败 episodes 是
结果账本的原料(物理世界当裁判)。
"""

from __future__ import annotations

from typing import Any, Protocol


class MemoryIface(Protocol):
    def read(self, query_hidden: Any, k: int = 5) -> list[Any]:
        """读回:返回隐状态向量序列,兼作触发层唤醒信号(rt/gate)。"""
        ...

    def write(self, hidden: Any, surprise: float, meta: dict | None = None) -> None:
        """写入:由触发层的 surprise 门控决定(rt/gate.should_write_memory)。"""
        ...


class ExternalMemory:
    """默认实现:向量库存隐状态快照 + 明文摘要(供审计,不进主循环)。"""

    def __init__(self, backend: Any = None):
        self.backend = backend  # MVP 可接 mem0;生产可接 Qdrant/Neo4j

    def read(self, query_hidden: Any, k: int = 5) -> list[Any]:
        raise NotImplementedError

    def write(self, hidden: Any, surprise: float, meta: dict | None = None) -> None:
        raise NotImplementedError
