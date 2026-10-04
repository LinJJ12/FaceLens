"""视频分析链路成功路径测试（假模型 + 合成视频，不需要 TensorFlow 与真实权重）。"""
import io

import cv2
import numpy as np
import pytest

EMOTION_LABELS = ['anger', 'disgust', 'fear', 'happy', 'normal', 'sad', 'surprised']


class FakeKerasModel:
    """替代 Keras 模型：形状推断 + 固定概率输出（surprised 置信度最高）。"""

    input_shape = (None, 96, 96, 1)

    def predict(self, x, verbose=0):
        probs = np.full((1, len(EMOTION_LABELS)), 0.1, dtype=np.float32)
        probs[0, EMOTION_LABELS.index('surprised')] = 0.4  # 0.1*6 + 0.4 = 1.0
        return probs


@pytest.fixture()
def fake_model(app_module):
    entry = {'type': 'keras', 'obj': FakeKerasModel(), 'infer': None, 'input_shape': (96, 96, 1)}
    app_module.models['cnn'] = entry
    yield entry
    app_module.models.pop('cnn', None)


def _write_test_video(path, fps=10, seconds=3, size=(64, 64)):
    """生成纯色渐变的合成视频（无需真实人脸，仅打通推理管线）。"""
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(path), fourcc, fps, size)
    assert writer.isOpened(), '合成视频 VideoWriter 打开失败'
    for i in range(fps * seconds):
        color = int((i * 16) % 255)
        frame = np.full((size[1], size[0], 3), color, dtype=np.uint8)
        writer.write(frame)
    writer.release()


def test_video_upload_analyze_success(client, auth_headers, fake_model, app_module, tmp_path, monkeypatch):
    """上传 → 分析 → 历史一次性入库 + 健康表按情绪聚合更新。"""
    monkeypatch.setattr(app_module, 'UPLOAD_ROOT', tmp_path.resolve())
    monkeypatch.setattr(app_module, 'UPLOAD_FOLDER', tmp_path)
    monkeypatch.setattr(app_module.video_processor, 'upload_folder', str(tmp_path))

    # 合成 3 秒视频并上传
    tmp_video = tmp_path / 'src.mp4'
    _write_test_video(tmp_video)
    buf = io.BytesIO(tmp_video.read_bytes())
    buf.seek(0)

    resp = client.post('/api/video/upload', headers=auth_headers,
                       data={'video': (buf, 'test.mp4')},
                       content_type='multipart/form-data')
    assert resp.status_code == 200, resp.get_json()
    upload = resp.get_json()
    video_id = upload['video_id']
    assert video_id.startswith('u')  # 属主前缀
    assert upload['video_info']['duration'] > 0
    assert upload['thumbnail'].startswith('data:image')

    # 分析：3 秒视频按 1 秒间隔应产出 3 帧
    resp = client.post('/api/video/analyze', headers=auth_headers, json={
        'video_id': video_id, 'model': 'cnn', 'interval': 1.0, 'max_frames': 10,
    })
    assert resp.status_code == 200, resp.get_json()
    body = resp.get_json()
    assert body['success'] is True
    assert body['total_frames'] == 3
    assert len(body['frames']) == 3
    frame = body['frames'][0]
    assert frame['emotion'] == 'surprised'
    assert frame['original_frame'].startswith('data:image/jpeg')
    assert frame['face_image'].startswith('data:image')
    # timeline 只承载序列信息，不再重复携带图片，控制响应体
    assert 'original_frame' not in body['timeline']['timeline'][0]

    # 历史记录一次性入库（3 帧）
    hist = client.get('/api/histories', headers=auth_headers).get_json()
    assert hist['total'] == 3

    # 健康表按情绪聚合更新：3 帧同为 surprised → 单次调用计入 3（中性）
    me = client.get('/api/auth/me', headers=auth_headers).get_json()['user']
    from src.storage.database import UserEmotionSummary
    with app_module.app.app_context():
        summary = UserEmotionSummary.query.filter_by(username=me['username']).first()
        assert summary is not None
        assert summary.total_predictions == 3
        assert summary.neutral_count == 3
        assert summary.avg_confidence == pytest.approx(0.4)


def test_video_upload_rejects_oversize(client, auth_headers, app_module, tmp_path, monkeypatch):
    """超过上限的视频落盘后应被删除并返回 413。"""
    monkeypatch.setattr(app_module, 'UPLOAD_ROOT', tmp_path.resolve())
    monkeypatch.setattr(app_module, 'UPLOAD_FOLDER', tmp_path)
    monkeypatch.setattr(app_module.video_processor, 'upload_folder', str(tmp_path))
    monkeypatch.setitem(app_module.app.config, 'MAX_VIDEO_BYTES', 64)

    buf = io.BytesIO(b'x' * 256)
    buf.seek(0)
    resp = client.post('/api/video/upload', headers=auth_headers,
                       data={'video': (buf, 'big.mp4')},
                       content_type='multipart/form-data')
    assert resp.status_code == 413
    # 落盘的超限文件已被清理
    assert not list(tmp_path.glob('u*'))
