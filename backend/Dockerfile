# 推理后端 — Python 3.8 + TensorFlow 2.10.1（与本地验证环境一致）
# 构建上下文为仓库根目录: docker compose build backend

FROM python:3.8-slim-bullseye

WORKDIR /app

# 说明：使用 opencv-contrib-python-headless（无 GUI 依赖），不需要 apt 安装
# libgl/libsm 等 X11 库；Debian bullseye 已于 2026-08 结束 LTS、apt 源失效，
# 因此本镜像刻意保持零 apt 操作，避免构建失败。
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt \
    && pip install --no-cache-dir "tensorflow==2.10.1" gunicorn==21.2.0 \
    && pip install --no-cache-dir --no-deps "mtcnn==0.1.1"

COPY backend /app/backend

WORKDIR /app/backend
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN chmod +x /app/backend/docker-entrypoint.sh     && mkdir -p /app/backend/data     && useradd -m appuser     && chown -R appuser:appuser /app/backend

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=300s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/api/health')" || exit 1

ENTRYPOINT ["/app/backend/docker-entrypoint.sh"]
