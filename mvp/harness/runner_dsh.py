"""评测驱动:用 deepseek-harness-sdk 批量驱动 dsh agent 跑任务集。

流程:逐任务 harness.run(instruction) → judge.grade 判分 → traces.jsonl + results.json。
agent 循环、工具执行全部发生在 dsh 侧(工具来自 mvp-tools.js 插件,模型来自 vLLM);
本脚本只负责 驱动/判分/统计 —— 对应大架构的 forge/tracer 原型。

用法(机器上):
  python runner_dsh.py --tasks ../tasks/smoke_5.jsonl --out ../out/smoke
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from judge import grade  # noqa: E402


def load_tasks(path: str, limit: int) -> list[dict]:
    tasks = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
    return tasks[:limit] if limit else tasks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True, help="任务 jsonl 路径")
    ap.add_argument("--out", required=True, help="输出目录")
    ap.add_argument("--cordis", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "dsh-plugin", "cordis.yml"))
    ap.add_argument("--provider", default="local-vllm")
    ap.add_argument("--model", default="Qwen2.5-1.5B-Instruct")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    from deepseek_harness import DeepSeekHarness  # 装了 SDK 才 import

    tasks = load_tasks(args.tasks, args.limit)
    os.makedirs(args.out, exist_ok=True)
    trace_path = os.path.join(args.out, "traces.jsonl")
    results: list[dict] = []

    with DeepSeekHarness(
        provider=args.provider,
        model=args.model,
        cordis=os.path.abspath(args.cordis),
        cwd=os.path.dirname(os.path.abspath(args.tasks)),
        session_root=os.path.join(args.out, "sessions"),
    ) as harness:
        with open(trace_path, "w", encoding="utf-8") as tf:
            for i, task in enumerate(tasks):
                t0 = time.time()
                try:
                    run = harness.run(task["instruction"], session_id=task["id"])
                    answer = (run.final_response or "").strip()
                    finish = getattr(run, "finish_reason", "")
                except Exception as exc:  # 单任务失败不拖垮整批
                    answer, finish = f"ERROR: {exc}", "exception"
                latency = round(time.time() - t0, 2)
                ok = grade(task, answer)
                rec = {"id": task["id"], "tag": task["tag"], "ok": ok,
                       "answer": answer[:300], "gold": task["answer"],
                       "latency_s": latency, "finish": finish}
                results.append(rec)
                tf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                tf.flush()
                print(f"[{i + 1}/{len(tasks)}] {task['id']} {'PASS' if ok else 'FAIL'} "
                      f"({latency}s)", flush=True)

    report(args.out, results)


def report(out_dir: str, results: list[dict]) -> None:
    n = len(results) or 1
    metrics = {
        "n": len(results),
        "success_rate": round(sum(r["ok"] for r in results) / n, 4),
        "by_tag": {},
        "avg_latency_s": round(sum(r["latency_s"] for r in results) / n, 2),
    }
    tags: dict[str, list[int]] = {}
    for r in results:
        tags.setdefault(r["tag"].split(":")[0], []).append(r["ok"])
    metrics["by_tag"] = {t: {"n": len(v), "success_rate": round(sum(v) / len(v), 4)}
                         for t, v in tags.items()}
    path = os.path.join(out_dir, "results.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "results": results}, f, ensure_ascii=False, indent=1)
    print(json.dumps(metrics, ensure_ascii=False, indent=1))
    print(f"已写入 {path}")


if __name__ == "__main__":
    main()
