"""
配置文件 — 路径与运行参数的单一来源
"""
import os
import secrets
import warnings
from pathlib import Path

from dotenv import load_dotenv

# 读取 backend/.env（存在时），使本地 `python main.py` 与 Docker 行为一致
load_dotenv()

# backend/src/config -> backend/src -> backend -> project root
CONFIG_DIR = Path(__file__).resolve().parent
SRC_DIR = CONFIG_DIR.parent
BACKEND_DIR = SRC_DIR.parent
PROJECT_DIR = BACKEND_DIR.parent

# 运行时数据根（uploads / logs / db）
DATA_DIR = BACKEND_DIR / 'data'
UPLOAD_FOLDER = DATA_DIR / 'uploads'
LOG_DIR = DATA_DIR / 'logs'
DB_DIR = DATA_DIR / 'db'
SQLITE_PATH = DB_DIR / 'emotion_recognition.db'

# 模型目录（仓库根下）
MODEL_DIR = PROJECT_DIR / 'models'
MODEL_CONFIG = {
    'cnn': {
        'path': MODEL_DIR / 'RAF_CNN_83_best_model.h5',
        'description': 'CNN基础模型',
        'accuracy': 0.8377
    },
    'vgg': {
        'path': MODEL_DIR / 'RAF_VGG_80_best_model.h5',
        'description': 'VGG16迁移学习模型',
        'accuracy': 0.8000
    },
    'se81': {
        'path': MODEL_DIR / 'RAF_SE_81_saved_model',
        'description': 'SE注意力机制模型',
        'accuracy': 0.8100
    },
    'se83': {
        'path': MODEL_DIR / 'RAF_SE_83_saved_model',
        'description': 'SE注意力机制模型(最佳)',
        'accuracy': 0.8300
    }
}

# 对外推理路径（字符串，供 load / 状态接口使用）
MODEL_PATHS = {name: str(cfg['path']) for name, cfg in MODEL_CONFIG.items()}

# 服务器配置
HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
PORT = int(os.environ.get('FLASK_PORT', '5000'))
DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() in ('1', 'true', 'yes')

# 上传限制
MAX_CONTENT_LENGTH = 200 * 1024 * 1024   # 请求体上限（与视频上限一致）
MAX_IMAGE_BYTES = 16 * 1024 * 1024       # 单张图像（base64 解码后）
MAX_VIDEO_BYTES = 200 * 1024 * 1024      # 单个视频

# 数据库配置（`or` 兜底空字符串，避免 docker-compose 传入空值导致启动崩溃）
DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{SQLITE_PATH.as_posix()}'

# JWT 配置（auth 模块从这里取，避免多处默认值不一致）
_WEAK_SECRETS = {
    '',
    'your-secret-key-change-in-production',
    'change-me-in-production',
    'please-change-me-to-a-long-random-string',
}
_raw_secret = os.environ.get('JWT_SECRET_KEY') or ''
if _raw_secret in _WEAK_SECRETS:
    if _raw_secret:
        warnings.warn(
            'JWT_SECRET_KEY 仍为公开的示例默认值，任何人都可以伪造令牌；'
            '请在 .env / 环境变量中设置强随机密钥。',
            UserWarning,
            stacklevel=1,
        )
    # 未配置时使用进程级随机密钥：比公开常量安全（重启后旧令牌失效属预期行为）
    JWT_SECRET_KEY = secrets.token_urlsafe(48)
else:
    JWT_SECRET_KEY = _raw_secret

# CORS 允许来源（逗号分隔；默认 * 保持本地开发开箱即用）
CORS_ORIGINS = [o.strip() for o in os.environ.get('CORS_ORIGINS', '*').split(',') if o.strip()]

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': LOG_DIR / 'app.log'
}

# ==================== 情绪标签与分类口径（全后端唯一来源） ====================
# 与模型输出顺序一致
EMOTION_LABELS = ['anger', 'disgust', 'fear', 'happy', 'normal', 'sad', 'surprised']
EMOTION_LABELS_CN = ['生气', '厌恶', '害怕', '高兴', '平静', '悲伤', '惊讶']

EMOTION_EN_TO_CN = dict(zip(EMOTION_LABELS, EMOTION_LABELS_CN))
EMOTION_CN_TO_EN = {v: k for k, v in EMOTION_EN_TO_CN.items()}

# 积极 / 消极 / 中性口径（与前端 Analysis.vue / Health.vue 保持一致）
POSITIVE_EMOTIONS = ('happy', 'normal')
NEGATIVE_EMOTIONS = ('anger', 'sad', 'fear', 'disgust')
NEUTRAL_EMOTIONS = ('surprised',)


def classify_emotion(emotion_en: str) -> str:
    """返回情绪的极性分类：positive / negative / neutral（未知返回 unknown）。"""
    if emotion_en in POSITIVE_EMOTIONS:
        return 'positive'
    if emotion_en in NEGATIVE_EMOTIONS:
        return 'negative'
    if emotion_en in NEUTRAL_EMOTIONS:
        return 'neutral'
    return 'unknown'


# 情绪效价映射（1=最消极 ... 7=最积极），用于稳定性计算（与前端 emotionMap 一致）
EMOTION_VALENCE = {
    'anger': 1, 'disgust': 2, 'fear': 3, 'sad': 4,
    'normal': 5, 'surprised': 6, 'happy': 7,
}

# 确保目录存在
for _dir in (UPLOAD_FOLDER, LOG_DIR, DB_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
