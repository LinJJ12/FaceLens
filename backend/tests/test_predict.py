"""预测链路测试（注入假模型，不需要 TensorFlow 与真实权重）。"""
import base64
import io

import numpy as np
import pytest
from PIL import Image

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


def _png_data_url(size=(200, 200), color=(120, 120, 120)):
    buf = io.BytesIO()
    Image.new('RGB', size, color).save(buf, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def test_predict_requires_loaded_model(client, auth_headers):
    """无权重环境下模型加载失败应返回 500 而不是崩溃。"""
    resp = client.post('/api/predict', headers=auth_headers, json={
        'image': _png_data_url(), 'model': 'vgg', 'detect_face': False,
    })
    assert resp.status_code == 500
    assert '模型加载失败' in resp.get_json()['error']


def test_predict_rejects_bad_payload(client, auth_headers, fake_model):
    # 缺少 image
    assert client.post('/api/predict', headers=auth_headers, json={}).status_code == 400
    # 不支持的模型
    resp = client.post('/api/predict', headers=auth_headers, json={
        'image': _png_data_url(), 'model': 'nope',
    })
    assert resp.status_code == 400
    # 非图像 base64
    bad = base64.b64encode(b'this is not an image').decode()
    resp = client.post('/api/predict', headers=auth_headers, json={
        'image': bad, 'model': 'cnn',
    })
    assert resp.status_code == 400


def test_predict_success_and_history(client, auth_headers, fake_model, app_module, tmp_path, monkeypatch):
    """端到端预测：返回结构、历史入库、健康表按百分数更新。"""
    monkeypatch.setattr(app_module, 'UPLOAD_ROOT', tmp_path.resolve())
    monkeypatch.setattr(app_module, 'UPLOAD_FOLDER', tmp_path)

    resp = client.post('/api/predict', headers=auth_headers, json={
        'image': _png_data_url(), 'model': 'cnn', 'detect_face': False,
    })
    assert resp.status_code == 200, resp.get_json()
    body = resp.get_json()
    assert body['success'] is True
    assert body['emotion'] == 'surprised'
    assert body['emotion_cn'] == '惊讶'
    assert body['confidence'] == pytest.approx(0.4)
    assert body['history_id']
    assert set(body['probabilities'].keys()) == set(EMOTION_LABELS)
    assert body['face_quality']['score'] >= 0

    # 历史记录已入库且归属当前用户
    headers = auth_headers
    hist = client.get('/api/histories', headers=headers)
    assert hist.status_code == 200
    items = hist.get_json()['histories']
    assert len(items) == 1
    assert items[0]['emotion'] == 'surprised'
    assert items[0]['input_type'] == 'image'

    # 健康评估已生成：占比为百分数、surprised 归类中性
    token = headers['Authorization'].split(' ')[1]
    me = client.get('/api/auth/me', headers=headers).get_json()['user']
    from src.storage.database import UserEmotionSummary, HealthAssessment
    with app_module.app.app_context():
        summary = UserEmotionSummary.query.filter_by(username=me['username']).first()
        assert summary is not None
        assert summary.total_predictions == 1
        assert summary.neutral_count == 1  # surprised → 中性
        assert summary.positive_rate == 0.0
        assert 0 <= summary.positive_rate <= 100

        assessment = HealthAssessment.query.filter_by(username=me['username']).first()
        assert assessment is not None
        assert assessment.health_score is not None
        assert assessment.alert_title  # 两种字段方案合一


def test_predict_health_assessment_upserted_per_day(client, auth_headers, fake_model, app_module, tmp_path, monkeypatch):
    """同一天多次预测只应有一条健康评估与汇总记录。"""
    monkeypatch.setattr(app_module, 'UPLOAD_ROOT', tmp_path.resolve())
    monkeypatch.setattr(app_module, 'UPLOAD_FOLDER', tmp_path)

    for _ in range(3):
        resp = client.post('/api/predict', headers=auth_headers, json={
            'image': _png_data_url(), 'model': 'cnn', 'detect_face': False,
        })
        assert resp.status_code == 200

    token = auth_headers['Authorization'].split(' ')[1]
    me = client.get('/api/auth/me', headers=auth_headers).get_json()['user']
    from src.storage.database import UserEmotionSummary, HealthAssessment
    with app_module.app.app_context():
        assert UserEmotionSummary.query.filter_by(username=me['username']).count() == 1
        assert HealthAssessment.query.filter_by(username=me['username']).count() == 1
        summary = UserEmotionSummary.query.filter_by(username=me['username']).first()
        assert summary.total_predictions == 3


def test_batch_predict(client, auth_headers, fake_model, app_module, tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, 'UPLOAD_ROOT', tmp_path.resolve())
    monkeypatch.setattr(app_module, 'UPLOAD_FOLDER', tmp_path)

    good = _png_data_url()
    bad = base64.b64encode(b'not-an-image').decode()
    resp = client.post('/api/batch_predict', headers=auth_headers, json={
        'images': [good, bad, good], 'model': 'cnn', 'detect_face': False,
    })
    assert resp.status_code == 200
    results = resp.get_json()['results']
    assert len(results) == 3
    assert 'emotion' in results[0]
    assert 'error' in results[1]      # 非法图像被逐项报告
    assert 'emotion' in results[2]
    assert results[0]['history_id']

    # 批量预测同样入库并更新健康表
    hist = client.get('/api/histories', headers=auth_headers).get_json()
    assert hist['total'] == 2


def test_video_analyze_validates_params(client, auth_headers, fake_model):
    resp = client.post('/api/video/analyze', headers=auth_headers, json={
        'video_id': 'whatever.mp4', 'interval': 0, 'max_frames': 10,
    })
    assert resp.status_code == 400
    assert 'interval' in resp.get_json()['error']

    resp = client.post('/api/video/analyze', headers=auth_headers, json={
        'video_id': 'whatever.mp4', 'interval': 5, 'max_frames': 100000,
    })
    assert resp.status_code == 400


def test_video_analyze_blocks_missing_file(client, auth_headers):
    resp = client.post('/api/video/analyze', headers=auth_headers, json={
        'video_id': 'no_such_video.mp4',
    })
    assert resp.status_code == 404
