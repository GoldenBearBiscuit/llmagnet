#!/usr/bin/env bash
# 参考组件一键重克隆(浅克隆;Phase 0 不需要,Phase 1 起按需执行)
cd "$(dirname "$0")/refs" || exit 1
for repo in \
  "https://github.com/microsoft/agent-lightning.git" \
  "https://github.com/Gen-Verse/LatentMAS.git" \
  "https://github.com/facebookresearch/coconut.git" \
  "https://github.com/microsoft/Mage.git" \
  "https://github.com/mem0ai/mem0.git"; do
  name=$(basename "$repo" .git)
  [ -d "$name/.git" ] && echo "skip $name" && continue
  git clone --depth 1 "$repo"
done
