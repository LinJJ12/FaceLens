"""
更新用户情绪汇总和健康评估记录的时间字段（危险操作：重写全部时间戳，需显式传入 --yes）
将所有记录的 updated_at 和 created_at 设置为当前时间
"""

import sys
import _bootstrap  # noqa: F401
from src.storage.database import db, UserEmotionSummary, HealthAssessment
from src.api.app import app
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if '--yes' not in sys.argv:
    print('⚠️  该脚本会把所有记录的时间戳重写为当前时间，破坏原有时间线。')
    print('    确认执行请运行: python scripts/update_timestamps.py --yes')
    sys.exit(1)

def update_timestamps():
    """更新所有记录的时间戳为当前时间"""
    with app.app_context():
        try:
            current_time = datetime.now()
            
            # 更新用户情绪汇总表
            summaries = UserEmotionSummary.query.all()
            summary_count = 0
            for summary in summaries:
                summary.updated_at = current_time
                summary_count += 1
            
            logger.info(f"✅ 已更新 {summary_count} 条用户情绪汇总记录的时间戳")
            
            # 更新健康评估表
            assessments = HealthAssessment.query.all()
            assessment_count = 0
            for assessment in assessments:
                assessment.created_at = current_time
                assessment.updated_at = current_time
                assessment_count += 1
            
            logger.info(f"✅ 已更新 {assessment_count} 条健康评估记录的时间戳")
            
            # 提交所有更改
            db.session.commit()
            logger.info("✅ 所有时间戳更新已提交到数据库")
            
            return True
                
        except Exception as e:
            logger.error(f"❌ 更新时间戳时发生错误: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("开始更新用户情绪汇总和健康评估记录的时间字段...")
    print("=" * 60)
    
    try:
        update_timestamps()
        print("\n✅ 时间戳更新完成！")
        print("\n提示：新创建的记录将自动使用正确的时间戳")
    except Exception as e:
        print(f"\n❌ 更新失败: {e}")
        exit(1)
