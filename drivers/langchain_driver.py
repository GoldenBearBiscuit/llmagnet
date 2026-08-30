"""langchain 驱动(骨架)。

实现 ForgeDriver 四函数契约(list_tools / emit_tool_call / report_reward /
stream_trace)。接入深度三档:
  第 0 档  base_url 指向 lf serve(零代码,只有 -O3 权重收益)
  第 1 档  本 driver:内循环委托给 rt/(全收益,明文只剩 fork 边界)
  第 2 档  框架暴露 DAG(LCEL 节点/角色转换点),编译器做更细 credit assignment
参考:refs/agent-lightning 对 langchain 的集成方式。
"""
