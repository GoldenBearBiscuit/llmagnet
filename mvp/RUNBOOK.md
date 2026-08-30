# RUNBOOK — 云机部署执行手册(LLMagnet MVP Phase 0)

> 原则:本机只写代码/生成数据,云机只照本手册按序执行。
> 每步都有「验证」小节,验证不过不要进下一步。
> 预算纪律见 PLAN.md §6(上限 ¥6000,Phase 0 全程 <¥10)。

---

## 步骤总览

```
本机:生成任务集 → 上传代码
云机:① 初始化环境 → ② 下载模型 → ③ 起 vLLM → ④ 冒烟 → ⑤ Phase 0 基线 → ⑥ 回传结果 → ⑦ 关机
```

---

## 本机准备(做一次)

1. 生成任务集(纯标准库,无需装任何东西):
   ```bash
   cd D:\Project\llmagnet\mvp\tasks
   python generate_data.py
   ```
   验证:产出 `kb.json`、`train_300.jsonl`(300 条)、`golden_50.jsonl`(50 条)、`smoke_5.jsonl`(5 条)。
2. 需要上传的目录:
   ```
   llmagnet/mvp/            # 全部(harness、tasks、dsh-plugin、requirements.txt、RUNBOOK)
   dsh/examples/headless-agent/cordis.yml   # 参考模板(排障用,见云机步骤 ④-2)
   ```

---

## 云机 ①:实例初始化(开机后 ~5 分钟)

```bash
# 1) 环境变量(追加进 ~/.bashrc,一次性)
cat >> ~/.bashrc <<'EOF'
export DATA=/root/autodl-tmp/llmagnet
export HF_HOME=/root/autodl-tmp/hf
export HF_ENDPOINT=https://hf-mirror.com
export PATH=$PATH:/root/autodl-tmp/bin
EOF
source ~/.bashrc
mkdir -p $DATA/models $DATA/out $DATA/bin

# 2) Python 依赖(torch 2.8 已预装,严禁动 torch)
cd /root/autodl-tmp/llmagnet/mvp
pip install -r requirements.txt

# 3) 验证
nvidia-smi                       # 应看到 RTX 3090 24GB
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
python -c "import transformers, vllm, deepseek_harness; print('deps ok')"
```

**验证**:三行命令都无报错。

## 云机 ②:拉取代码(git)

```bash
# AutoDL 开 GitHub 加速;Gitee/国内网络可跳过这行
source /etc/network_turbo 2>/dev/null
git clone https://github.com/GoldenBearBiscuit/llmagnet.git /root/autodl-tmp/llmagnet
unset http_proxy https_proxy 2>/dev/null

# 私有仓库需一次性登录:Settings → Developer settings → PAT(token 勾 repo 权限),
# clone 时用户名填 GitHub 用户名、密码贴 token。
```

**验证**:云机 `ls /root/autodl-tmp/llmagnet/mvp` 能看到 harness/tasks/dsh-plugin。

## 云机 ③:下载模型(~3GB,走镜像,约 3-5 分钟)

```bash
hf download Qwen/Qwen2.5-1.5B-Instruct --local-dir $DATA/models/qwen2.5-1.5b
# 老版本 huggingface_cli 命令名:huggingface-cli download ...(等价)
```

**验证**:`ls $DATA/models/qwen2.5-1.5b` 有 `config.json`、`*.safetensors`。

## 云机 ④:起 vLLM 模型服务(tmux 常驻)

```bash
export VLLM_API_KEY=local-dev
tmux new -s vllm
vllm serve $DATA/models/qwen2.5-1.5b --served-model-name Qwen2.5-1.5B-Instruct \
  --port 8000 --max-model-len 8192
# Ctrl+B D 退出 tmux(服务继续跑)
```

**验证**(另开终端):
```bash
curl -s http://127.0.0.1:8000/v1/models | head -c 300
# 应返回含 "Qwen2.5-1.5B-Instruct" 的 JSON
```

### ④-2 配置核对(dsh 侧)

```bash
export MVP_KB_PATH=/root/autodl-tmp/llmagnet/mvp/tasks/kb.json   # 写进 ~/.bashrc
# 组合格式核对:dsh 处于预览期,若步骤⑤冒烟报 cordis/包名错误,
# 对比官方模板修正 cordis.yml(已随仓库带好):
#   /root/autodl-tmp/llmagnet/mvp/dsh-plugin/reference-headless-cordis.yml
```

## 云机 ⑤:冒烟测试(~5 分钟,先别看成功率)

```bash
cd /root/autodl-tmp/llmagnet/mvp/harness
python runner_dsh.py --tasks ../tasks/smoke_5.jsonl --out ../out/smoke
```

**通过标准**:
- 5 条任务全部执行完,无 exception;
- `out/smoke/traces.jsonl` 有 5 行记录;
- 若有 FAIL:人工看 answer 字段——是模型答错(正常,基线的意义)还是格式/工具没调起来(要排障)。

排障速查:
| 症状 | 处置 |
|---|---|
| cordis 组合/包名报错 | 用 ④-2 的参考模板合并修正 cordis.yml |
| 报 @deepseek-ai/dsh-tools 解析失败 | 在 dsh-plugin 目录 `npm i @deepseek-ai/dsh-tools` 建本地 node_modules,再试 |
| 连不上 127.0.0.1:8000 | tmux 里 vLLM 没起来,回去看日志 |
| run 超时/卡死 | 确认 `export VLLM_API_KEY` 在当前 shell 生效 |

## 云机 ⑥:Phase 0 基线(vLLM 加持下 ~1-2h)

```bash
cd /root/autodl-tmp/llmagnet/mvp/harness
# 训练集 300 条(这个结果可用于后续 RFT/探针)
nohup python runner_dsh.py --tasks ../tasks/train_300.jsonl --out ../out/phase0-train \
  > ../out/phase0-train.log 2>&1 &
# 完成后再跑封存金标集
python runner_dsh.py --tasks ../tasks/golden_50.jsonl --out ../out/phase0-golden
```

**产出**:`out/phase0-train/results.json`(成功率/分 tag 指标/均时延)+ traces.jsonl。

## 云机 ⑦:看结果 + 回传本机

```bash
# 机器上快速看
python -m json.tool ../out/phase0-train/results.json | head -40
```

```bash
# 本机拉回(端口/主机替换)
scp -rP <端口> root@<host>:/root/autodl-tmp/llmagnet/out  D:\Project\llmagnet\mvp\out
```

回传后在 `reports/phase0.md` 记一页:成功率(总体/分 tag)、失败分桶(工具没调/参数错/推理错)、平均时延。
**失败案例就是 Phase 2 探针的训练数据和评测集种子,一个都别扔。**

## 云机 ⑧:计费纪律

- Phase 0 全部完成 → 确认 `out/` 已回传本机 → 面板**关机**(只收磁盘费)。
- 数据盘内容常驻,下次开机接着跑 Phase 1,不用重下模型。
- 长跑一律 nohup + tmux,SSH 断线不影响。

---

## 后续阶段(Phase 1-4)执行手册占位

Phase 1(蒸馏)/ Phase 2(探针)/ Phase 3(fork)/ Phase 4(RFT+GRPO)的 RUNBOOK
在各自阶段代码就位后补写,格式与本手册一致:本机写好 → 上传 → 按序执行 → 回传报告。
