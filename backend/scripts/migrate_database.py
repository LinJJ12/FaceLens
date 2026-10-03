"""
完整的数据库迁移脚本（幂等，可安全重复执行）
1. 添加 UserEmotionSummary 缺失的字段
2. 添加 HealthAssessment 缺失的字段
3. 仅当显式传入 --reset-data 时才清理旧数据（避免重复运行误删统计数据）
"""
import sqlite3
import os
import sys
from _db_path import resolve_db_path

def migrate(reset_data=False):
    db_path = str(resolve_db_path())

    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("=" * 60)
        print("开始数据库迁移...")
        print("=" * 60)
        
        # ========== 1. UserEmotionSummary 表 ==========
        print("\n【1/3】检查 user_emotion_summary 表...")
        cursor.execute("PRAGMA table_info(user_emotion_summary)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"  当前字段: {len(columns)} 个")
        
        # 添加缺失字段
        if 'emotion_counts' not in columns:
            print("  + 添加 emotion_counts 字段...")
            cursor.execute("ALTER TABLE user_emotion_summary ADD COLUMN emotion_counts TEXT")
            print("    ✅ 已添加")
        
        if 'dominant_emotion_count' not in columns:
            print("  + 添加 dominant_emotion_count 字段...")
            cursor.execute("ALTER TABLE user_emotion_summary ADD COLUMN dominant_emotion_count INTEGER DEFAULT 0")
            print("    ✅ 已添加")
        
        # ========== 2. HealthAssessment 表 ==========
        print("\n【2/3】检查 health_assessment 表...")
        cursor.execute("PRAGMA table_info(health_assessment)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"  当前字段: {len(columns)} 个")
        
        # 添加缺失字段
        fields_to_add = [
            ('health_score', 'INTEGER'),
            ('risk_level', 'VARCHAR(20)'),
            ('risk_level_cn', 'VARCHAR(20)'),
            ('emotion_stability', 'FLOAT'),
            ('based_on_days', 'INTEGER DEFAULT 1')
        ]
        
        for field_name, field_type in fields_to_add:
            if field_name not in columns:
                print(f"  + 添加 {field_name} 字段...")
                cursor.execute(f"ALTER TABLE health_assessment ADD COLUMN {field_name} {field_type}")
                print(f"    ✅ 已添加")
        
        # ========== 3. 可选的数据清理（仅显式传入 --reset-data 时执行） ==========
        print("\n【3/3】数据清理检查...")

        # 统计现有数据
        cursor.execute("SELECT COUNT(*) FROM user_emotion_summary")
        summary_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM health_assessment")
        assessment_count = cursor.fetchone()[0]

        print(f"  user_emotion_summary: {summary_count} 条记录")
        print(f"  health_assessment: {assessment_count} 条记录")

        if summary_count > 0 or assessment_count > 0:
            if reset_data:
                print("\n  --reset-data 已指定，执行清理...")
                cursor.execute("DELETE FROM user_emotion_summary")
                cursor.execute("DELETE FROM health_assessment")
                print("  ✅ 已清理旧数据")
                print("  提示：重新上传图片识别后会自动生成新格式的数据")
            else:
                print("\n  跳过数据清理（保留现有统计数据）。")
                print("  如确需清空这两张表重新生成，请显式运行: python scripts/migrate_database.py --reset-data")
        
        conn.commit()
        print("\n" + "=" * 60)
        print("✅ 数据库迁移完成！")
        print("=" * 60)
        print("\n下一步：")
        print("1. 重启 Flask 服务器")
        print("2. 在前端上传图片进行识别测试")
        print("3. 查看数据库表数据")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate(reset_data='--reset-data' in sys.argv)
