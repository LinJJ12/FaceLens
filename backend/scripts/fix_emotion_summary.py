"""
修复情绪汇总表的数据（危险操作：清空整表，需显式传入 --yes）
清除旧的不一致数据，让用户重新进行情绪识别来生成正确的数据
"""
import sys
import _bootstrap  # noqa: F401
from src.storage.database import db, UserEmotionSummary
from src.api.app import app

if '--yes' not in sys.argv:
    print('⚠️  该脚本会清空 user_emotion_summary 全表。')
    print('    确认执行请运行: python scripts/fix_emotion_summary.py --yes')
    sys.exit(1)

with app.app_context():
    try:
        # 删除所有旧的情绪汇总记录
        deleted = UserEmotionSummary.query.delete()
        db.session.commit()
        
        print(f"✅ 已删除 {deleted} 条旧的情绪汇总记录")
        print("\n📝 下一步操作：")
        print("1. 重启 Flask 后端服务（确保新代码生效）")
        print("2. 登录用户进行情绪识别")
        print("3. 新的识别结果会自动创建正确格式的情绪汇总记录")
        print("4. 在管理界面查看更新后的情绪汇总数据")
        
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        db.session.rollback()
