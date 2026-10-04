"""
pytest 公共夹具。

关键设计：
- 测试环境不安装 TensorFlow（推理依赖在 CI / 开发机可选），conftest 在导入 app 前
  注入一个最小的 tensorflow 桩模块，仅覆盖 app.py 导入期用到的名字。
  桩不会伪造推理能力——模型加载会真实失败，需要推理的测试自行注入假模型对象。
- 每个测试会话使用独立的临时 SQLite 数据库，不触碰 backend/data/。
"""
import os
import sys
import tempfile
import types
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# ---- 环境变量必须在导入 src.* 之前设置 ----
_TMP_DIR = tempfile.mkdtemp(prefix='facelens_test_')
os.environ.setdefault('JWT_SECRET_KEY', 'facelens-test-secret-key-not-for-production')
os.environ['DATABASE_URL'] = f'sqlite:///{Path(_TMP_DIR) / "test.db"}'
os.environ.setdefault('CORS_ORIGINS', '*')

# ---- TensorFlow 桩（仅当真实 TF 不可用时） ----
try:
    import tensorflow  # noqa: F401
    HAVE_TENSORFLOW = True
except Exception:
    HAVE_TENSORFLOW = False

    def _install_tensorflow_stub():
        tf_stub = types.ModuleType('tensorflow')
        tf_stub.__version__ = '0.0-stub'

        saved_model = types.ModuleType('tensorflow.saved_model')

        def _load_fail(path):
            raise IOError(f'TensorFlow 未安装（测试桩）：无法加载 {path}')

        saved_model.load = _load_fail
        tf_stub.saved_model = saved_model
        tf_stub.saved_model_load = _load_fail
        tf_stub.constant = lambda x: x

        keras_mod = types.ModuleType('tensorflow.keras')
        keras_models = types.ModuleType('tensorflow.keras.models')

        def _load_model_fail(path):
            raise IOError(f'TensorFlow 未安装（测试桩）：无法加载 {path}')

        keras_models.load_model = _load_model_fail
        keras_mod.models = keras_models
        tf_stub.keras = keras_mod

        sys.modules['tensorflow'] = tf_stub
        sys.modules['tensorflow.saved_model'] = saved_model
        sys.modules['tensorflow.keras'] = keras_mod
        sys.modules['tensorflow.keras.models'] = keras_models

    _install_tensorflow_stub()

import pytest  # noqa: E402


@pytest.fixture(scope='session')
def app_module():
    """导入完整的 Flask app 模块（含数据库初始化）。"""
    import src.api.app as app_module
    return app_module


@pytest.fixture(scope='session')
def app(app_module):
    """Flask 应用实例。"""
    app = app_module.app
    # 默认关闭限流，避免用例间共享计数导致误伤；限流行为在专门用例中开启验证
    app_module.limiter.enabled = False
    return app


@pytest.fixture()
def client(app):
    """Flask 测试客户端。"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def _unique_suffix():
    import time
    import random
    return f"{int(time.time() * 1000)}{random.randint(100, 999)}"


@pytest.fixture()
def user_token(client):
    """注册一个随机用户并返回 (token, username)。"""
    username = f'user{_unique_suffix()}'
    resp = client.post('/api/auth/register', json={
        'username': username,
        'email': f'{username}@example.com',
        'password': 'password123',
    })
    assert resp.status_code == 201, resp.get_json()
    token = resp.get_json()['token']
    return token, username


@pytest.fixture()
def auth_headers(user_token):
    token, _ = user_token
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture()
def admin_headers(app_module, client):
    """使用内置演示管理员账号登录。"""
    resp = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123',
    })
    assert resp.status_code == 200, resp.get_json()
    token = resp.get_json()['token']
    return {'Authorization': f'Bearer {token}'}
