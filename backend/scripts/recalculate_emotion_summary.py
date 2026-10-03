"""
重新计算情绪汇总数据（运维脚本）
根据预测历史记录重新生成指定用户、指定日期的情绪汇总，口径与后端保持一致：
- 积极 = happy/normal，消极 = anger/sad/fear/disgust，中性 = surprised
- positive_rate / negative_rate 为 0-100 百分数

用法:
    python scripts/recalculate_emotion_summary.py [username] [YYYY-MM-DD]
默认: admin 今天
"""
import sys
from datetime import date, datetime

import _bootstrap  # noqa: F401
from src.config.settings import (
    EMOTION_EN_TO_CN,
    EMOTION_CN_TO_EN,
    POSITIVE_EMOTIONS,
    NEGATIVE_EMOTIONS,
)
from src.storage.database import db, UserEmotionSummary, PredictionHistory
from src.api.app import app
from collections import Counter

username = sys.argv[1] if len(sys.argv) > 1 else 'admin'
if len(sys.argv) > 2:
    target_day = datetime.fromisoformat(sys.argv[2]).date()
else:
    target_day = date.today()

with app.app_context():
    try:
        # 先删除该用户当天的情绪汇总（重新计算）
        UserEmotionSummary.query.filter_by(
            username=username,
            summary_date=target_day
        ).delete()
        db.session.commit()

        print(f"✅ 已清除 {username} {target_day} 的旧汇总数据")

        today_predictions = PredictionHistory.query.filter(
            PredictionHistory.username == username,
            db.func.date(PredictionHistory.created_at) == target_day
        ).order_by(PredictionHistory.created_at).all()

        print(f"\n📊 找到 {len(today_predictions)} 条预测记录：")

        if not today_predictions:
            print("❌ 没有找到预测记录")
            sys.exit(0)

        # 统计情绪分布
        emotion_counts = Counter()
        confidences = []

        for pred in today_predictions:
            print(f"  - {pred.emotion_cn} (置信度: {pred.confidence:.2%})")
            emotion_counts[pred.emotion_cn] += 1
            confidences.append(pred.confidence)

        print(f"\n📈 情绪分布: {dict(emotion_counts)}")

        # 计算主导情绪
        dominant_emotion_cn = emotion_counts.most_common(1)[0][0]
        dominant_emotion_count = emotion_counts[dominant_emotion_cn]

        # 积极/消极/中性（与后端 settings.py 口径一致）
        positive_en = set(POSITIVE_EMOTIONS)
        negative_en = set(NEGATIVE_EMOTIONS)

        positive_count = sum(
            emotion_counts.get(EMOTION_EN_TO_CN[e], 0) for e in positive_en
        )
        negative_count = sum(
            emotion_counts.get(EMOTION_EN_TO_CN[e], 0) for e in negative_en
        )
        neutral_count = sum(
            c for cn, c in emotion_counts.items()
            if EMOTION_CN_TO_EN.get(cn) not in positive_en | negative_en
        )

        total = len(today_predictions)
        avg_confidence = sum(confidences) / total if confidences else 0

        # 创建新的汇总记录（占比为百分数）
        summary = UserEmotionSummary(
            username=username,
            summary_date=target_day,
            total_predictions=total,
            dominant_emotion=EMOTION_CN_TO_EN.get(dominant_emotion_cn, dominant_emotion_cn),
            dominant_emotion_cn=dominant_emotion_cn,
            dominant_emotion_count=dominant_emotion_count,
            emotion_counts=dict(emotion_counts),
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            positive_rate=round(positive_count / total * 100, 2) if total > 0 else 0,
            negative_rate=round(negative_count / total * 100, 2) if total > 0 else 0,
            avg_confidence=round(avg_confidence, 2)
        )

        db.session.add(summary)
        db.session.commit()

        print(f"\n✅ 已创建新的情绪汇总记录：")
        print(f"  总识别次数: {total}")
        print(f"  主导情绪: {dominant_emotion_cn} (出现 {dominant_emotion_count} 次)")
        print(f"  积极次数: {positive_count}")
        print(f"  消极次数: {negative_count}")
        print(f"  中性次数: {neutral_count}")
        print(f"  平均置信度: {avg_confidence:.2%}")
        print(f"\n🎉 请刷新管理界面查看更新后的数据！")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
