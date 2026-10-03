"""
后端启动入口。在 backend/ 目录下运行: python main.py
也可从仓库任意目录: python backend/main.py
"""
import logging
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.config.settings import HOST, PORT, DEBUG  # noqa: E402
# 导入 app 即完成日志（控制台+文件）与数据库初始化
from src.api.app import app, warmup_models  # noqa: E402

logger = logging.getLogger(__name__)


def main():
    logger.info("🚀 正在启动人脸情绪识别服务...")
    warmup_models()
    logger.info(f"🌐 服务启动在 http://{HOST}:{PORT}")
    # 生产环境请关闭 debug 并使用 WSGI 容器部署（见 docker-entrypoint.sh + gunicorn.conf.py）
    app.run(host=HOST, port=PORT, debug=DEBUG)


if __name__ == '__main__':
    main()
