"""判分器(纯标准库)。

数值题:从答案文本里抽最后一个数字,容差 max(0.05, 0.1%)——
容忍模型回答"实付金额是 284.05 元"这类自然语言包装。
文本题:归一化后做包含匹配(答出关键词即算对)。
"""

from __future__ import annotations

import re

_NUM = re.compile(r"-?\d+(?:\.\d+)?")
_NORM = re.compile(r"[\s,。.,;；::'\"()（）\[\]【】]")


def extract_number(text: str) -> float | None:
    hits = _NUM.findall(str(text).replace(",", "").replace("，", ""))
    return float(hits[-1]) if hits else None


def _norm(s: str) -> str:
    return _NORM.sub("", str(s)).lower()


def grade(task: dict, answer: str) -> int:
    """返回 1/0。task 需含 answer / answer_type 字段。"""
    if not answer or str(answer).startswith("ERROR"):
        return 0
    if task.get("answer_type") == "number":
        got = extract_number(answer)
        if got is None:
            return 0
        want = float(task["answer"])
        return int(abs(got - want) <= max(0.05, abs(want) * 0.001))
    return int(_norm(task["answer"]) in _norm(answer))
