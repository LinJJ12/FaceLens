"""
心理健康API模块
提供心理健康评估、工具使用记录、建议交互等接口
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from src.storage.database import (
    db, 
    PredictionHistory, 
    UserEmotionSummary,
    HealthAssessment,
    EmotionJournal,
    GratitudeRecord
)
from src.auth import token_required
import logging
from sqlalchemy import func

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__, url_prefix='/api/health')


# ========================================
# 健康评级辅助函数（app.py 的 update_health_tables 与本模块共用）
# positive_rate / negative_rate 统一为 0-100 百分数
# ========================================

def health_score_to_level(score):
    """健康得分 -> (risk_level, risk_level_cn, 主建议)。与前端 Analysis.vue 阈值一致。"""
    if score >= 85:
        return 'excellent', '优秀', '您的情绪状态非常健康！保持积极乐观的心态，继续加油！'
    if score >= 70:
        return 'good', '良好', '您的情绪状态良好，继续保持规律作息和适度运动。'
    if score >= 55:
        return 'normal', '一般', '建议多参与社交活动，尝试放松技巧，如冥想、瑜伽等。'
    return 'need-attention', '需要关注', '您的情绪波动较大，建议咨询专业心理咨询师，及时调整心态。'


def positive_rate_to_alert(positive_rate, negative_rate):
    """积极占比(%) -> (alert_title, alert_type, alert_description, suggestions)。与前端 Health.vue 口径一致。"""
    if positive_rate >= 70:
        return (
            '✨ 心理状态良好',
            'success',
            f'您最近 {positive_rate}% 的时间保持积极情绪，心理健康状态优秀！',
            [
                '继续保持当前的生活方式和心态',
                '可以尝试帮助身边情绪低落的朋友',
                '定期回顾让你开心的事物，建立感恩日记',
                '保持规律的运动和充足的睡眠'
            ]
        )
    if positive_rate >= 40:
        return (
            '⚖️ 情绪状态平衡',
            'warning',
            f'您的积极情绪占 {positive_rate}%，消极情绪占 {negative_rate}%，整体处于平衡状态。',
            [
                '尝试增加积极活动，如运动、社交、爱好',
                '学习情绪管理技巧，提升情绪调节能力',
                '每天记录3件让你感恩的事情',
                '遇到压力时及时寻求支持和帮助'
            ]
        )
    return (
        '⚠️ 需要关注情绪健康',
        'error',
        f'您最近 {negative_rate}% 的时间处于消极情绪，建议重视心理健康。',
        [
            '建议咨询专业心理咨询师获得支持',
            '每天安排30分钟放松时间，如冥想、散步',
            '与信任的朋友或家人分享感受',
            '尝试认知行为疗法（CBT）技巧调整思维模式',
            '保持规律作息，避免熬夜和过度劳累'
        ]
    )


def _parse_date_param(raw):
    """解析 ISO 日期参数，非法时抛 ValueError（由调用方转 400）。"""
    if isinstance(raw, str):
        return datetime.fromisoformat(raw).date()
    return raw


# ========================================
# 情绪统计汇总接口
# ========================================

@health_bp.route('/emotion-summary', methods=['GET'])
@token_required
def get_emotion_summary():
    """
    获取用户情绪统计汇总
    参数: date (可选，默认今天), days (可选，查询天数，默认1)
    """
    try:
        username = request.current_user['username']
        target_date = request.args.get('date', date.today().isoformat())
        days = request.args.get('days', 1, type=int)

        try:
            target_date = _parse_date_param(target_date)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'date 参数格式非法，应为 YYYY-MM-DD'}), 400
        if days < 1 or days > 365:
            return jsonify({'success': False, 'error': 'days 参数需在 1-365 之间'}), 400

        # 如果请求多天数据
        if days > 1:
            start_date = target_date - timedelta(days=days-1)
            summaries = UserEmotionSummary.query.filter(
                UserEmotionSummary.username == username,
                UserEmotionSummary.summary_date >= start_date,
                UserEmotionSummary.summary_date <= target_date
            ).order_by(UserEmotionSummary.summary_date.desc()).all()

            return jsonify({
                'success': True,
                'summaries': [s.to_dict() for s in summaries],
                'data': [s.to_dict() for s in summaries]
            })

        # 单日数据
        summary = UserEmotionSummary.query.filter_by(
            username=username,
            summary_date=target_date
        ).first()

        # 如果没有汇总数据，实时计算
        if not summary:
            summary = generate_emotion_summary(username, target_date)

        return jsonify({
            'success': True,
            'summaries': [summary.to_dict()] if summary else [],
            'data': summary.to_dict() if summary else None
        })

    except Exception as e:
        logger.error(f"获取情绪汇总失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def generate_emotion_summary(username, target_date):
    """
    实时生成情绪汇总数据
    """
    try:
        # 查询当天的预测记录（按时间排序，保证情绪变化率统计确定性）
        records = PredictionHistory.query.filter(
            PredictionHistory.username == username,
            func.date(PredictionHistory.created_at) == target_date
        ).order_by(PredictionHistory.created_at).all()

        if not records:
            return None

        # 计算统计数据
        total = len(records)
        positive_count = sum(1 for r in records if r.emotion in ['happy', 'normal'])
        negative_count = sum(1 for r in records if r.emotion in ['anger', 'sad', 'fear', 'disgust'])
        neutral_count = sum(1 for r in records if r.emotion == 'surprised')

        # 主导情绪
        emotion_counts = {}
        for r in records:
            emotion_counts[r.emotion] = emotion_counts.get(r.emotion, 0) + 1
        dominant_emotion = max(emotion_counts, key=emotion_counts.get)

        # 平均置信度
        avg_confidence = sum(r.confidence for r in records) / total

        # 情绪波动 - 标准差
        emotion_map = {'anger': 1, 'disgust': 2, 'fear': 3, 'sad': 4, 'normal': 5, 'surprised': 6, 'happy': 7}
        emotion_values = [emotion_map.get(r.emotion, 5) for r in records]
        mean = sum(emotion_values) / len(emotion_values)
        variance = sum((v - mean) ** 2 for v in emotion_values) / len(emotion_values)
        stddev = variance ** 0.5

        # 情绪变化率（基于全部记录，分母为实际比较次数）
        emotion_changes = sum(
            1 for i in range(1, len(records)) if records[i].emotion != records[i - 1].emotion
        )
        change_rate = (emotion_changes / max(1, len(records) - 1)) * 100 if len(records) > 1 else 0
        
        # 稳定性等级
        stability_score = max(0, 100 - change_rate)
        if stability_score >= 70:
            stability_level = '稳定'
        elif stability_score >= 40:
            stability_level = '一般'
        else:
            stability_level = '波动较大'
        
        # 活跃天数（查询历史总天数）
        active_days_count = db.session.query(
            func.count(func.distinct(func.date(PredictionHistory.created_at)))
        ).filter(PredictionHistory.username == username).scalar()
        
        # 保存到数据库
        summary = UserEmotionSummary(
            username=username,
            summary_date=target_date,
            total_predictions=total,
            dominant_emotion=dominant_emotion,
            dominant_emotion_cn=get_emotion_cn(dominant_emotion),
            avg_confidence=round(avg_confidence, 4),
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            positive_rate=round((positive_count / total) * 100, 2),
            negative_rate=round((negative_count / total) * 100, 2),
            stability_stddev=round(stddev, 2),
            stability_change_rate=round(change_rate, 2),
            stability_level=stability_level,
            active_days=active_days_count
        )
        
        # 注意：这里必须用 add + commit。merge 返回的是新的持久化实例，
        # 原对象不会获得数据库默认值（如 created_at），后续 to_dict() 会因 None 崩溃
        db.session.add(summary)
        db.session.commit()
        
        return summary
        
    except Exception as e:
        logger.error(f"生成情绪汇总失败: {e}")
        db.session.rollback()
        return None


# ========================================
# 心理健康评估接口
# ========================================

@health_bp.route('/assessment', methods=['GET'])
@token_required
def get_health_assessment():
    """
    获取心理健康评估
    """
    try:
        username = request.current_user['username']
        target_date = request.args.get('date', date.today().isoformat())

        try:
            target_date = _parse_date_param(target_date)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'date 参数格式非法，应为 YYYY-MM-DD'}), 400

        assessment = HealthAssessment.query.filter_by(
            username=username,
            assessment_date=target_date
        ).first()
        
        # 如果没有评估，生成一个
        if not assessment:
            assessment = generate_health_assessment(username, target_date)
        
        return jsonify({
            'success': True,
            'assessments': [assessment.to_dict()] if assessment else [],
            'data': assessment.to_dict() if assessment else None
        })
        
    except Exception as e:
        logger.error(f"获取健康评估失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def generate_health_assessment(username, target_date):
    """
    生成心理健康评估
    """
    try:
        # 先获取或生成情绪汇总
        summary = UserEmotionSummary.query.filter_by(
            username=username,
            summary_date=target_date
        ).first()
        
        if not summary:
            summary = generate_emotion_summary(username, target_date)
        
        if not summary:
            return None
        
        positive_rate = summary.positive_rate
        negative_rate = summary.negative_rate
        total = summary.total_predictions

        # 生成评估内容
        alert_title, alert_type, alert_description, suggestions = positive_rate_to_alert(
            positive_rate, negative_rate
        )

        # 健康得分（与 update_health_tables / 前端公式一致）
        stability_stddev = summary.stability_stddev or 0.0
        stability = max(0, min(100, 100 - stability_stddev * 20))
        health_score = int(round(
            (positive_rate or 0) * 0.4 + (100 - (negative_rate or 0)) * 0.3 + stability * 0.3
        ))
        health_score = max(0, min(100, health_score))
        risk_level, risk_level_cn, _ = health_score_to_level(health_score)

        # 保存评估
        assessment = HealthAssessment(
            username=username,
            assessment_date=target_date,
            health_score=health_score,
            risk_level=risk_level,
            risk_level_cn=risk_level_cn,
            alert_title=alert_title,
            alert_type=alert_type,
            alert_description=alert_description,
            suggestions=suggestions,
            positive_rate=positive_rate,
            negative_rate=negative_rate,
            emotion_stability=round(stability / 100.0, 4),
            stability_level=summary.stability_level
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        return assessment
        
    except Exception as e:
        logger.error(f"生成健康评估失败: {e}")
        db.session.rollback()
        return None


# ========================================
# 情绪日记接口
# ========================================

@health_bp.route('/journal', methods=['POST'])
@token_required
def save_journal():
    """
    保存情绪日记
    Body: {
        content: '日记内容',
        emotion: 'happy',  // 可选
        emotion_cn: '高兴'  // 可选
    }
    """
    try:
        username = request.current_user['username']
        data = request.get_json()
        
        content = data.get('content', '').strip()
        if not content:
            return jsonify({'success': False, 'error': '日记内容不能为空'}), 400
        
        journal = EmotionJournal(
            username=username,
            content=content,
            emotion=data.get('emotion'),
            emotion_cn=data.get('emotion_cn')
        )
        
        db.session.add(journal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '日记已保存',
            'data': journal.to_dict()
        })
        
    except Exception as e:
        logger.error(f"保存日记失败: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@health_bp.route('/journal', methods=['GET'])
@token_required
def get_journals():
    """
    获取情绪日记列表
    参数: limit (可选，默认50), offset (可选，默认0)
    """
    try:
        username = request.current_user['username']
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        journals = EmotionJournal.query.filter_by(
            username=username
        ).order_by(
            EmotionJournal.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        total = EmotionJournal.query.filter_by(username=username).count()
        
        return jsonify({
            'success': True,
            'data': [j.to_dict() for j in journals],
            'total': total
        })
        
    except Exception as e:
        logger.error(f"获取日记列表失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@health_bp.route('/journal/<int:journal_id>', methods=['GET'])
@token_required
def get_journal(journal_id):
    """获取单条日记详情"""
    try:
        username = request.current_user['username']
        
        journal = EmotionJournal.query.filter_by(
            id=journal_id,
            username=username
        ).first()
        
        if not journal:
            return jsonify({'success': False, 'error': '日记不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': journal.to_dict()
        })
        
    except Exception as e:
        logger.error(f"获取日记详情失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@health_bp.route('/journal/<int:journal_id>', methods=['PUT'])
@token_required
def update_journal(journal_id):
    """
    更新日记
    Body: {
        content: '更新后的内容'
    }
    """
    try:
        username = request.current_user['username']
        data = request.get_json()
        
        journal = EmotionJournal.query.filter_by(
            id=journal_id,
            username=username
        ).first()
        
        if not journal:
            return jsonify({'success': False, 'error': '日记不存在'}), 404
        
        content = data.get('content', '').strip()
        if not content:
            return jsonify({'success': False, 'error': '日记内容不能为空'}), 400
        
        journal.content = content
        if 'emotion' in data:
            journal.emotion = data['emotion']
        if 'emotion_cn' in data:
            journal.emotion_cn = data['emotion_cn']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '日记已更新',
            'data': journal.to_dict()
        })
        
    except Exception as e:
        logger.error(f"更新日记失败: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@health_bp.route('/journal/<int:journal_id>', methods=['DELETE'])
@token_required
def delete_journal(journal_id):
    """删除日记"""
    try:
        username = request.current_user['username']
        
        journal = EmotionJournal.query.filter_by(
            id=journal_id,
            username=username
        ).first()
        
        if not journal:
            return jsonify({'success': False, 'error': '日记不存在'}), 404
        
        db.session.delete(journal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '日记已删除'
        })
        
    except Exception as e:
        logger.error(f"删除日记失败: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ========================================
# 感恩记录接口
# ========================================

@health_bp.route('/gratitude', methods=['POST'])
@token_required
def save_gratitude():
    """保存感恩记录"""
    try:
        username = request.current_user['username']
        data = request.json
        
        if not data or 'items' not in data:
            return jsonify({'success': False, 'error': '缺少必要字段'}), 400
        
        # 过滤空项
        items = [item.strip() for item in data['items'] if item and item.strip()]
        
        if not items:
            return jsonify({'success': False, 'error': '请至少写一件感恩的事'}), 400
        
        # 创建感恩记录
        gratitude = GratitudeRecord(
            username=username,
            items=items
        )
        
        db.session.add(gratitude)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '感恩记录已保存',
            'data': gratitude.to_dict()
        })
        
    except Exception as e:
        logger.error(f"保存感恩记录失败: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@health_bp.route('/gratitude', methods=['GET'])
@token_required
def get_gratitudes():
    """获取感恩记录列表"""
    try:
        username = request.current_user['username']
        limit = request.args.get('limit', 50, type=int)
        
        gratitudes = GratitudeRecord.query.filter_by(
            username=username
        ).order_by(
            GratitudeRecord.created_at.desc()
        ).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [g.to_dict() for g in gratitudes]
        })
        
    except Exception as e:
        logger.error(f"获取感恩记录失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@health_bp.route('/gratitude/<int:gratitude_id>', methods=['GET'])
@token_required
def get_gratitude(gratitude_id):
    """获取单条感恩记录"""
    try:
        username = request.current_user['username']
        
        gratitude = GratitudeRecord.query.filter_by(
            id=gratitude_id,
            username=username
        ).first()
        
        if not gratitude:
            return jsonify({'success': False, 'error': '记录不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': gratitude.to_dict()
        })
        
    except Exception as e:
        logger.error(f"获取感恩记录失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@health_bp.route('/gratitude/<int:gratitude_id>', methods=['DELETE'])
@token_required
def delete_gratitude(gratitude_id):
    """删除感恩记录"""
    try:
        username = request.current_user['username']
        
        gratitude = GratitudeRecord.query.filter_by(
            id=gratitude_id,
            username=username
        ).first()
        
        if not gratitude:
            return jsonify({'success': False, 'error': '记录不存在'}), 404
        
        db.session.delete(gratitude)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '感恩记录已删除'
        })
        
    except Exception as e:
        logger.error(f"删除感恩记录失败: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ========================================
# 辅助函数
# ========================================

def get_emotion_cn(emotion):
    """英文情绪转中文"""
    emotion_map = {
        'anger': '生气',
        'disgust': '厌恶',
        'fear': '害怕',
        'happy': '高兴',
        'normal': '平静',
        'sad': '悲伤',
        'surprised': '惊讶'
    }
    return emotion_map.get(emotion, emotion)
