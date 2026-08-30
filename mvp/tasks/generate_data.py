"""任务集与知识库生成器(纯标准库,本机直接跑,无需任何依赖)。

产出 4 个文件(与脚本同目录):
  kb.json          知识库(商品/优惠券/订单/城市距离)
  train_300.jsonl  训练任务(训练侧可见)
  golden_50.jsonl  封存金标集(训练侧不可见——红线 #2)
  smoke_5.jsonl    冒烟测试 5 条
全部任务程序判分;随机种子固定,任何机器重跑结果一致。

用法:python generate_data.py
"""

from __future__ import annotations

import json
import os
import random

SEED = 20260830
random.seed(SEED)

HERE = os.path.dirname(os.path.abspath(__file__))

PRODUCT_NAMES = [
    "无线鼠标", "机械键盘", "升降桌", "显示器支架", "USB-C 扩展坞", "降噪耳机",
    "电动水杯", "桌面加湿器", "笔记本支架", "无线充电板", "蓝牙音箱", "摄像头遮光罩",
    "人体工学椅", "桌面理线器", "4K 显示器", "便携打印机", "指纹密码锁", "智能台灯",
    "空气炸锅", "破壁机", "扫地机器人", "加湿器滤芯", "咖啡手磨", "保温饭盒",
    "瑜伽垫", "筋膜枪", "露营灯", "折叠桌椅", "车载支架", "行车记录仪",
    "电热毯", "挂烫机", "电子墨水屏", "桌面粉碎机", "铁观音茶叶", "落地灯",
    "电煮锅", "颈椎按摩仪", "折叠购物车", "防蓝光眼镜",
]
CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "西安", "南京", "重庆", "天津", "苏州"]
N_COUPONS, N_ORDERS = 24, 400


def build_kb() -> dict:
    products = {
        name: {"price": random.choice([49, 59, 79, 99, 129, 159, 199, 249, 299, 399, 499, 699]),
               "category": random.choice(["外设", "家具", "家电", "数码", "出行"])}
        for name in PRODUCT_NAMES
    }
    coupons = {
        f"CPN{i:03d}": {"percent_off": random.choice([5, 10, 15, 20]),
                        "min_spend": random.choice([100, 200, 300, 500])}
        for i in range(1, N_COUPONS + 1)
    }
    orders = {}
    for i in range(1, N_ORDERS + 1):
        orders[f"SO-{i:04d}"] = {
            "product": random.choice(PRODUCT_NAMES),
            "qty": random.randint(1, 9),
            "coupon": random.choice([None] + list(coupons.keys())),
        }
    distances = {}
    for i, a in enumerate(CITIES):
        for b in CITIES[i + 1:]:
            distances[f"{a}-{b}"] = random.randint(300, 2000)
    return {"products": products, "coupons": coupons,
            "orders": orders, "distances": distances}


def round2(x: float) -> float:
    return round(x + 1e-9, 2)


# ── 任务构造器:每个返回 {id, tag, instruction, answer, answer_type, tools} ──

def t_calc(tag: str, idx: int) -> dict:
    style = random.choice(["add_mul", "mul_sub", "div_exact"])
    if style == "add_mul":
        a, b, c = random.randint(11, 99), random.randint(2, 9), random.randint(2, 9)
        expr, ans = f"({a}+{b})*{c}", (a + b) * c
    elif style == "mul_sub":
        a, b, c = random.randint(21, 99), random.randint(2, 30), random.randint(10, 99)
        expr, ans = f"{a}*{b}-{c}", a * b - c
    else:
        b, q = random.randint(3, 19), random.randint(3, 30)
        a, c = b * q, random.randint(2, 50)
        expr, ans = f"{a}/{b}+{c}", q + c
    return {"id": f"{tag}-calc-{idx:03d}", "tag": "arithmetic",
            "instruction": f"请计算:{expr} = ?",
            "answer": str(ans), "answer_type": "number"}


def t_lookup_price(tag: str, idx: int, kb: dict) -> dict:
    name = random.choice(PRODUCT_NAMES)
    return {"id": f"{tag}-lp-{idx:03d}", "tag": "lookup",
            "instruction": f"商品「{name}」的单价是多少元?",
            "answer": str(kb["products"][name]["price"]), "answer_type": "number"}


def t_lookup_order_product(tag: str, idx: int, kb: dict) -> dict:
    oid = f"SO-{random.randint(1, N_ORDERS):04d}"
    return {"id": f"{tag}-lo-{idx:03d}", "tag": "lookup",
            "instruction": f"订单 {oid} 购买的商品名称是什么?",
            "answer": kb["orders"][oid]["product"], "answer_type": "text"}


def t_lookup_coupon(tag: str, idx: int, kb: dict) -> dict:
    code = f"CPN{random.randint(1, N_COUPONS):03d}"
    return {"id": f"{tag}-lc-{idx:03d}", "tag": "lookup",
            "instruction": f"优惠券 {code} 的折扣是百分之几?(只回答数字)",
            "answer": str(kb["coupons"][code]["percent_off"]), "answer_type": "number"}


def t_lookup_dist(tag: str, idx: int, kb: dict) -> dict:
    a, b = random.sample(CITIES, 2)
    key = f"{a}-{b}" if f"{a}-{b}" in kb["distances"] else f"{b}-{a}"
    return {"id": f"{tag}-ld-{idx:03d}", "tag": "lookup",
            "instruction": f"从{a}到{b}的距离是多少公里?",
            "answer": str(kb["distances"][key]), "answer_type": "number"}


def t_twohop_order_total(tag: str, idx: int, kb: dict) -> dict:
    """订单 → 商品单价 × 数量 = 原价合计(强制 order→product→calculator 三步)。"""
    oid = f"SO-{random.randint(1, N_ORDERS):04d}"
    o = kb["orders"][oid]
    total = round2(kb["products"][o["product"]]["price"] * o["qty"])
    return {"id": f"{tag}-ht-{idx:03d}", "tag": "twohop",
            "instruction": f"订单 {oid} 共购买{o['qty']}件商品。请计算该订单的原始总价(单价×数量,不打折)是多少元?",
            "answer": str(total), "answer_type": "number"}


def t_twohop_coupon_pay(tag: str, idx: int, kb: dict) -> dict:
    """订单 → 单价×数量 → 查券 → 判断满减门槛 → 实付(最长链路,考验触发层)。"""
    oid = f"SO-{random.randint(1, N_ORDERS):04d}"
    o = kb["orders"][oid]
    code = o["coupon"] or random.choice(list(kb["coupons"].keys()))
    c = kb["coupons"][code]
    total = kb["products"][o["product"]]["price"] * o["qty"]
    payable = total * (1 - c["percent_off"] / 100) if total >= c["min_spend"] else total
    return {"id": f"{tag}-hc-{idx:03d}", "tag": "twohop",
            "instruction": (f"订单 {oid} 购买了{o['qty']}件商品,使用优惠券 {code} 结算。"
                            f"请计算实付金额是多少元?(优惠券规则:满 {c['min_spend']} 元减 {c['percent_off']}%)"),
            "answer": str(round2(payable)), "answer_type": "number"}


def t_twohop_freight(tag: str, idx: int, kb: dict) -> dict:
    """距离 → 运费(两跳计算)。"""
    a, b = random.sample(CITIES, 2)
    key = f"{a}-{b}" if f"{a}-{b}" in kb["distances"] else f"{b}-{a}"
    d = kb["distances"][key]
    return {"id": f"{tag}-hf-{idx:03d}", "tag": "twohop",
            "instruction": f"从{a}到{b}的货运运费按每公里 0.5 元计,这趟运费是多少元?",
            "answer": str(round2(d * 0.5)), "answer_type": "number"}


def make_set(tag: str, n: int, kb: dict, exclude: set[str] | None = None) -> list[dict]:
    """按权重 20% 算术 / 30% 单查 / 50% 多步 生成 n 条,撞重复自动补抽。"""
    exclude = exclude or set()
    builders = {
        "calc": lambda i: t_calc(tag, i),
        "lp": lambda i: t_lookup_price(tag, i, kb),
        "lo": lambda i: t_lookup_order_product(tag, i, kb),
        "lc": lambda i: t_lookup_coupon(tag, i, kb),
        "ld": lambda i: t_lookup_dist(tag, i, kb),
        "ht": lambda i: t_twohop_order_total(tag, i, kb),
        "hc": lambda i: t_twohop_coupon_pay(tag, i, kb),
        "hf": lambda i: t_twohop_freight(tag, i, kb),
    }
    weights = {"calc": 20, "lp": 10, "lo": 8, "lc": 6, "ld": 6,
               "ht": 20, "hc": 15, "hf": 15}
    kinds, w = list(weights), list(weights.values())
    seen, out, counters = set(), [], {}
    guard = 0
    while len(out) < n and guard < n * 50:
        guard += 1
        kind = random.choices(kinds, weights=w)[0]
        i = counters.get(kind, 0)
        counters[kind] = i + 1
        task = dict(builders[kind](i))
        if task["instruction"] in seen or task["instruction"] in exclude:
            counters[kind] -= 1
            continue
        seen.add(task["instruction"])
        task["tools"] = ["calculator", "kb_query"]
        out.append(task)
    return out


def main() -> None:
    kb = build_kb()
    train = make_set("tr", 300, kb)
    golden = make_set("gd", 50, kb, exclude={t["instruction"] for t in train})
    smoke = make_set("sm", 5, kb, exclude={t["instruction"] for t in train})

    def dump(name: str, rows: list[dict]) -> None:
        path = os.path.join(HERE, name)
        with open(path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"  {name}: {len(rows)} 条")

    print("生成任务集(种子 %d):" % SEED)
    with open(os.path.join(HERE, "kb.json"), "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=1)
    print("  kb.json: %d 商品 / %d 券 / %d 订单 / %d 距离" %
          (len(kb["products"]), len(kb["coupons"]), len(kb["orders"]), len(kb["distances"])))
    dump("train_300.jsonl", train)
    dump("golden_50.jsonl", golden)
    dump("smoke_5.jsonl", smoke)
    print("完成。golden_50 请视为封存金标集(不要用于任何训练/调参)。")


if __name__ == "__main__":
    main()
