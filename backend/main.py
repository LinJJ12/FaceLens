"""
后端启动入口。在 backend/ 目录下运行: python main.py
也可从仓库任意目录: python backend/main.py
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.api.app import app, warmup_models
from src.config.settings import HOST, PORT, LOG_DIR

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT
)
# 同步写入文件，供管理后台"系统日志"查看
_file_handler = RotatingFileHandler(
    LOG_DIR / 'app.log', maxBytes=2 * 1024 * 1024, backupCount=3, encoding='utf-8'
)
_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logging.getLogger().addHandler(_file_handler)
logger = logging.getLogger(__name__)


def main():
    logger.info("🚀 正在启动人脸情绪识别服务...")
    warmup_models()
    logger.info(f"🌐 服务启动在 http://{HOST}:{PORT}")
    # 生产环境请关闭 debug 并使用 WSGI 容器部署
    app.run(host=HOST, port=PORT, debug=False)


if __name__ == '__main__':
    main()
