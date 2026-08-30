// mvp-tools.js — LLMagnet MVP 的 dsh 工具插件(纯 JS ESM,无 TS 编译依赖)。
// 注册两个工具:calculator(安全算术)与 kb_query(知识库查询)。
// 换任务 = 换插件/换 kb.json,评测驱动(runner_dsh.py)不用动。
//
// 知识库路径从环境变量 MVP_KB_PATH 读取(由 RUNBOOK 步骤 6 注入)。

import fs from 'node:fs'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'mvp-tools'
export const inject = ['tools']

// 只允许数字与四则运算符——杜绝 Function 注入面
const EXPR_OK = /^[0-9+\-*/().\s]+$/

function safeCalc(expr) {
  if (typeof expr !== 'string' || !EXPR_OK.test(expr) || expr.length > 200) {
    throw new Error(`非法表达式: ${expr}`)
  }
  const val = Function(`"use strict"; return (${expr})`)()
  if (typeof val !== 'number' || !Number.isFinite(val)) throw new Error('结果不是有限数')
  return val
}

export function apply(ctx) {
  const kbPath = process.env.MVP_KB_PATH
  if (!kbPath || !fs.existsSync(kbPath)) {
    throw new Error(`MVP_KB_PATH 未设置或文件不存在: ${kbPath}`)
  }
  const kb = JSON.parse(fs.readFileSync(kbPath, 'utf-8'))

  ctx.tools.register(defineTool({
    name: 'calculator',
    description: '计算算术表达式(支持 + - * / 和括号)。所有数值计算必须使用本工具。',
    parameters: {
      expression: { type: 'string', required: true, description: '算术表达式,例如 "3*4+2"' },
    },
    async execute(args) {
      const result = safeCalc(args.expression)
      return { result }
    },
  }))

  ctx.tools.register(defineTool({
    name: 'kb_query',
    description: '查询知识库。collection 取值: products(商品,key=商品名) / coupons(优惠券,key=券码) / orders(订单,key=订单号) / distances(城市距离,key="城市A-城市B")。',
    parameters: {
      collection: { type: 'string', required: true, description: 'products | coupons | orders | distances' },
      key: { type: 'string', required: true, description: '该集合下的键名' },
    },
    async execute(args) {
      const record = kb?.[args.collection]?.[String(args.key)] ?? null
      return { found: record !== null, record }
    },
  }))
}
