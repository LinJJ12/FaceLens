"""上传路径安全辅助函数测试（直接测试 app 模块的真实实现，目录隔离到 tmp）。"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def test_safe_user_dirname(app_module):
    assert app_module._safe_user_dirname('alice') == 'alice'
    assert '/' not in app_module._safe_user_dirname('a/b')
    assert '\\' not in app_module._safe_user_dirname('a\\b')
    assert '..' not in app_module._safe_user_dirname('../../etc/passwd')
    # 空值兜底
    assert app_module._safe_user_dirname('') == 'anonymous'
    assert app_module._safe_user_dirname(None) == 'anonymous'


def test_resolve_upload_file_blocks_traversal(app_module, tmp_path, monkeypatch):
    root = tmp_path / 'uploads'
    (root / 'predictions' / 'demo').mkdir(parents=True)
    target = root / 'predictions' / 'demo' / 'face.jpg'
    target.write_bytes(b'x')
    monkeypatch.setattr(app_module, 'UPLOAD_ROOT', root.resolve())

    rel = app_module._to_upload_relpath(target)
    assert rel == 'predictions/demo/face.jpg'

    assert app_module._resolve_upload_file(rel) == target.resolve()
    assert app_module._resolve_upload_file('../predictions/demo/face.jpg') is None
    assert app_module._resolve_upload_file('predictions/../../settings.py') is None
    assert app_module._resolve_upload_file('/etc/passwd') is None
    assert app_module._resolve_upload_file('') is None
    assert app_module._resolve_upload_file('no/such/file.jpg') is None


def test_user_can_access_upload(app_module):
    owner = {'username': 'alice', 'role': 'user'}
    other = {'username': 'bob', 'role': 'user'}
    admin = {'username': 'admin', 'role': 'admin'}

    assert app_module._user_can_access_upload('predictions/alice/face.jpg', owner)
    assert not app_module._user_can_access_upload('predictions/alice/face.jpg', other)
    assert app_module._user_can_access_upload('predictions/bob/face.jpg', admin)
    # 不属于受管子目录的路径一律拒绝（admin 除外）
    assert not app_module._user_can_access_upload('secret.txt', owner)
