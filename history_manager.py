"""
AI摄影导师 - 历史记录管理模块
提供真实的后端数据持久化存储（SQLite）
"""
import os
import json
import sqlite3
from datetime import datetime


class HistoryManager:
    """历史记录管理器：使用SQLite进行真实数据持久化"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            app_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(app_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "history.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                filename TEXT NOT NULL,
                image_path TEXT NOT NULL,
                analysis_json TEXT NOT NULL,
                comment TEXT DEFAULT '',
                thumbnail_path TEXT DEFAULT '',
                rules_used TEXT DEFAULT '',
                style TEXT DEFAULT '专业',
                thirds_score INTEGER DEFAULT 0,
                symmetry_score INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def save_record(self, filename: str, image_path: str, analysis: dict,
                    comment: str, rules: list, style: str) -> int:
        """保存一条分析记录，返回记录ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        analyses = analysis.get("analyses", {})
        thirds_score = analyses.get("rule_of_thirds", {}).get("score", 0)
        sym = analyses.get("symmetry", {})
        symmetry_score = sym.get("overall_score", 0)

        cursor.execute("""
            INSERT INTO analysis_history 
            (timestamp, filename, image_path, analysis_json, comment, rules_used, style, thirds_score, symmetry_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, filename, image_path,
            json.dumps(analysis, ensure_ascii=False),
            comment, json.dumps(rules), style,
            thirds_score, symmetry_score
        ))
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id

    def get_all_records(self) -> list:
        """获取所有历史记录"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM analysis_history ORDER BY id DESC
        """)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        for row in rows:
            row["analysis"] = json.loads(row["analysis_json"])
            row["rules_used"] = json.loads(row["rules_used"]) if row["rules_used"] else []
        return rows

    def get_record_by_id(self, record_id: int) -> dict:
        """根据ID获取单条记录"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analysis_history WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            record = dict(row)
            record["analysis"] = json.loads(record["analysis_json"])
            record["rules_used"] = json.loads(record["rules_used"]) if record["rules_used"] else []
            return record
        return None

    def delete_record(self, record_id: int) -> bool:
        """删除单条记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analysis_history WHERE id = ?", (record_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    def clear_all(self) -> int:
        """清空所有记录，返回删除数量"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM analysis_history")
        count = cursor.fetchone()[0]
        cursor.execute("DELETE FROM analysis_history")
        conn.commit()
        conn.close()
        return count

    def get_statistics(self) -> dict:
        """获取统计数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM analysis_history")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(thirds_score), AVG(symmetry_score) FROM analysis_history")
        row = cursor.fetchone()
        avg_thirds = round(row[0], 1) if row[0] else 0
        avg_symmetry = round(row[1], 1) if row[1] else 0
        cursor.execute("SELECT MAX(thirds_score), MAX(symmetry_score) FROM analysis_history")
        row2 = cursor.fetchone()
        best_thirds = row2[0] or 0
        best_symmetry = row2[1] or 0
        conn.close()
        return {
            "total_analyses": total,
            "avg_thirds_score": avg_thirds,
            "avg_symmetry_score": avg_symmetry,
            "best_thirds_score": best_thirds,
            "best_symmetry_score": best_symmetry
        }

    def save_setting(self, key: str, value: str):
        """保存应用设置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)
        """, (key, value))
        conn.commit()
        conn.close()

    def get_setting(self, key: str, default: str = "") -> str:
        """获取应用设置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default
