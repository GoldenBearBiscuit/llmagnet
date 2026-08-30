"""LLMagnet 构建时:把「开源权重 LLM + 现成 agent」编译成「隐空间 agent」。

流水线:-O0 基线 → -O1 蒸馏(Coconut)→ -O2 fork(ICAE/RCC)→ -O3 RL(Lightning 范式)。
每个 pass 独立可回退,verify 逐级对 -O0 基线验收。
"""
