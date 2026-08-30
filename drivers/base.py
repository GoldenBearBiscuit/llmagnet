"""框架驱动契约:任何 agent 框架接入只需实现这 4 个函数(几百行)。

分层:框架仍拥有业务编排/guardrails/人机交互;driver 只做映射;
guardrails 永远留在第 0 档边界上,不进编译(审计底线 + 安全红线)。
"""

from __future__ import annotations

from typing import Any, Protocol


class ForgeDriver(Protocol):
    def list_tools(self) -> list[dict]:
        """框架工具注册表 → manifest tool schema(MCP 原生可直读)。"""
        ...

    def emit_tool_call(self, intent: Any) -> Any:
        """编译产物的工具意图 → 框架执行器执行。"""
        ...

    def report_reward(self, task_id: str, reward: float) -> None:
        """框架任务回调 → 训练器(forge/trainer)。"""
        ...

    def stream_trace(self) -> Any:
        """轨迹遥测(OpenTelemetry)→ forge/tracer。"""
        ...
