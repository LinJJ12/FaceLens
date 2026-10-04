"""
Flask 扩展实例（跨模块共享，避免 app.py 与蓝图之间循环导入）。

限流存储为进程内存：gunicorn 固定 workers=1（见 gunicorn.conf.py），
多 worker / 多实例部署时需改用 Redis 等共享存储，否则各进程独立计数。
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri="memory://",
)
