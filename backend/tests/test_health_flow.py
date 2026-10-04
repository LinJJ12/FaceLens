"""健康数据链路测试：分类口径、占比量纲、按天 upsert。"""
from datetime import date

import pytest


@pytest.fixture()
def health_ctx(app_module, app):
    from src.storage.database import db, UserEmotionSummary, HealthAssessment, PredictionHistory
    return app_module, app, db, UserEmotionSummary, HealthAssessment, PredictionHistory


def test_classification_constants():
    from src.config.settings import classify_emotion, EMOTION_CN_TO_EN
    assert classify_emotion('happy') == 'positive'
    assert classify_emotion('normal') == 'positive'
    assert classify_emotion('anger') == 'negative'
    assert classify_emotion('sad') == 'negative'
    assert classify_emotion('fear') == 'negative'
    assert classify_emotion('disgust') == 'negative'
    assert classify_emotion('surprised') == 'neutral'  # 与前端口径一致
    assert classify_emotion('unknown-x') == 'unknown'
    assert EMOTION_CN_TO_EN['惊讶'] == 'surprised'  # 不再是 surprise


def test_update_health_tables_scales_and_counts(health_ctx):
    app_module, app, db, UserEmotionSummary, HealthAssessment, _ = health_ctx
    from src.config.settings import EMOTION_EN_TO_CN

    with app.app_context():
        # 模拟一天内 4 次预测：2 积极(happy/normal) + 1 消极(anger) + 1 中性(surprised)
        calls = [('happy', 0.9), ('normal', 0.8), ('anger', 0.7), ('surprised', 0.6)]
        for emotion, conf in calls:
            app_module.update_health_tables(
                username='scale_user', emotion=emotion,
                emotion_cn=EMOTION_EN_TO_CN[emotion], confidence=conf,
            )

        summary = UserEmotionSummary.query.filter_by(username='scale_user').first()
        assert summary.total_predictions == 4
        assert summary.positive_count == 2
        assert summary.negative_count == 1
        assert summary.neutral_count == 1
        # 占比为 0-100 百分数
        assert summary.positive_rate == pytest.approx(50.0)
        assert summary.negative_rate == pytest.approx(25.0)

        # 每日评估仅一条，且两种字段方案字段齐全
        assessments = HealthAssessment.query.filter_by(username='scale_user').all()
        assert len(assessments) == 1
        a = assessments[0]
        assert a.health_score is not None
        assert a.alert_title
        assert a.alert_type in ('success', 'warning', 'error')
        assert isinstance(a.suggestions, list) and a.suggestions

        db.session.query(HealthAssessment).filter_by(username='scale_user').delete()
        db.session.query(UserEmotionSummary).filter_by(username='scale_user').delete()
        db.session.commit()


def test_health_score_formula(health_ctx):
    """全 happy 时得分应处于优秀区间，而不是被量纲错误拉满或压低。"""
    app_module, app, db, UserEmotionSummary, HealthAssessment, _ = health_ctx
    from src.config.settings import EMOTION_EN_TO_CN

    with app.app_context():
        for _ in range(3):
            app_module.update_health_tables(
                username='happy_user', emotion='happy',
                emotion_cn=EMOTION_EN_TO_CN['happy'], confidence=0.9,
            )
        a = HealthAssessment.query.filter_by(username='happy_user').first()
        assert a.health_score >= 85  # 积极占比 100%
        assert a.risk_level == 'excellent'

        db.session.query(HealthAssessment).filter_by(username='happy_user').delete()
        db.session.query(UserEmotionSummary).filter_by(username='happy_user').delete()
        db.session.commit()


def test_negative_day_triggers_attention(health_ctx):
    app_module, app, db, UserEmotionSummary, HealthAssessment, _ = health_ctx
    from src.config.settings import EMOTION_EN_TO_CN

    with app.app_context():
        for _ in range(4):
            app_module.update_health_tables(
                username='sad_user', emotion='sad',
                emotion_cn=EMOTION_EN_TO_CN['sad'], confidence=0.8,
            )
        a = HealthAssessment.query.filter_by(username='sad_user').first()
        assert a.negative_rate == pytest.approx(100.0)
        assert a.alert_type == 'error'
        assert a.health_score < 55

        db.session.query(HealthAssessment).filter_by(username='sad_user').delete()
        db.session.query(UserEmotionSummary).filter_by(username='sad_user').delete()
        db.session.commit()


def test_assessment_api_roundtrip(client, auth_headers, health_ctx):
    """/api/health/assessment 与汇总接口返回结构一致、量纲为百分数。"""
    app_module, app, db, UserEmotionSummary, HealthAssessment, PredictionHistory = health_ctx
    import datetime
    from src.config.settings import EMOTION_EN_TO_CN

    me = client.get('/api/auth/me', headers=auth_headers).get_json()['user']

    with app.app_context():
        for emotion in ('happy', 'happy', 'sad'):
            db.session.add(PredictionHistory(
                emotion=emotion, emotion_cn=EMOTION_EN_TO_CN[emotion],
                confidence=0.85, model_used='CNN', username=me['username'],
                created_at=datetime.datetime.now(), input_type='image',
            ))
        db.session.commit()

    today = date.today().isoformat()
    resp = client.get(f'/api/health/assessment?date={today}', headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()['data']
    assert data is not None
    assert 0 <= data['positive_rate'] <= 100
    assert data['alert_title']

    resp = client.get(f'/api/health/emotion-summary?date={today}', headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()['data']
    assert data['positive_rate'] == pytest.approx(66.67)
    assert data['negative_rate'] == pytest.approx(33.33)


def test_assessment_api_rejects_bad_date(client, auth_headers):
    resp = client.get('/api/health/assessment?date=not-a-date', headers=auth_headers)
    assert resp.status_code == 400


def test_sqlite_pragmas_applied(app):
    """WAL 与 busy_timeout 应在连接级生效（并发写安全的前提）。"""
    from src.storage.database import db

    with app.app_context():
        conn = db.engine.connect()
        try:
            mode = conn.execute(db.text('PRAGMA journal_mode')).scalar()
            timeout = conn.execute(db.text('PRAGMA busy_timeout')).scalar()
        finally:
            conn.close()
    assert str(mode).lower() == 'wal'
    assert int(timeout) == 30000
