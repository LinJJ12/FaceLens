#!/bin/sh
set -e

cd /app/backend

if [ ! -d /app/models ] || [ -z "$(ls -A /app/models 2>/dev/null)" ]; then
  echo "⚠️  警告: /app/models 为空或未挂载，推理接口可能无法加载模型。"
  echo "    请将权重放入仓库 models/ 目录，或在 docker compose 中正确挂载卷。"
fi

echo "🚀 启动 Gunicorn（on_starting 钩子内预热模型，首次启动可能较慢）..."
exec gunicorn -c gunicorn.conf.py "src.api.app:app"
