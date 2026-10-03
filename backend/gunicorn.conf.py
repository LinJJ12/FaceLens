"""Gunicorn 配置：master 进程启动时预热模型，worker fork 后直接继承，首次请求无需现场加载。"""
import logging


def on_starting(server):
    logger = logging.getLogger(__name__)
    logger.info("⏳ gunicorn on_starting: 预热模型（首次启动可能较慢）...")
    try:
        from src.api.app import warmup_models
        warmup_models()
    except Exception as e:  # 预热失败不阻断启动，请求时仍会按需加载
        logger.warning(f"模型预热失败，服务仍将启动（可在模型就绪后重试）: {e}")


bind = "0.0.0.0:5000"
workers = 1
threads = 4
timeout = 300
keepalive = 5
preload_app = True
