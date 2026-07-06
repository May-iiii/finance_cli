"""
简单记账本 — 数据库操作层
所有 SQL 操作集中在这里，包括建表、增删查、分类统计。
每个函数自己管理数据库连接（用完即关），不跨请求持有。
"""

import sqlite3
import pandas as pd
from config import DB_PATH, CATEGORIES


def init_database():
    """创建数据库和 records 表（只在第一次运行时执行）。"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            amount      REAL    NOT NULL CHECK(amount > 0),
            category    TEXT    NOT NULL CHECK(category IN ('餐饮','交通','购物','娱乐','居住','其他')),
            date        TEXT    NOT NULL,
            note        TEXT    DEFAULT '',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_record(amount: float, category: str, date_str: str, note: str) -> tuple[bool, str]:
    """
    添加一条账目记录。
    参数：
        amount   — 金额（> 0）
        category — 分类（必须是 CATEGORIES 之一）
        date_str — 日期字符串，格式 YYYY-MM-DD
        note     — 备注，可为空字符串
    返回：
        (成功标志, 提示消息)
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO records (amount, category, date, note) VALUES (?, ?, ?, ?)",
            (amount, category, date_str, note)
        )
        conn.commit()
        return True, "添加成功！"
    except sqlite3.Error as e:
        return False, f"数据库错误：{e}"
    finally:
        conn.close()


def get_records(month: str | None = None, category: str | None = None) -> pd.DataFrame:
    """
    查询账目记录，支持按月份和分类筛选。
    参数：
        month    — "YYYY-MM" 格式，如 "2026-07"；None 表示不按月份筛选
        category — 分类名称；None 或 "全部" 表示不按分类筛选
    返回：
        pandas DataFrame，包含 id, amount, category, date, note 五列
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        query = "SELECT id, amount, category, date, note FROM records WHERE 1=1"
        params: list = []

        if month:
            query += " AND strftime('%Y-%m', date) = ?"
            params.append(month)

        if category and category != "全部":
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY date DESC, id DESC"

        df = pd.read_sql_query(query, conn, params=params)
        return df
    finally:
        conn.close()


def get_record_by_id(record_id: int) -> dict | None:
    """
    根据 ID 查询单条记录（删除确认时用）。
    返回：记录字典，不存在时返回 None。
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, amount, category, date, note FROM records WHERE id = ?",
            (record_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "amount": row[1],
            "category": row[2],
            "date": row[3],
            "note": row[4],
        }
    finally:
        conn.close()


def delete_record(record_id: int) -> tuple[bool, str]:
    """
    按 ID 删除一条记录。
    先检查记录是否存在，不存在则返回错误提示。
    返回：(成功标志, 提示消息)
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()

        # 先查是否存在
        cursor.execute("SELECT id FROM records WHERE id = ?", (record_id,))
        if cursor.fetchone() is None:
            return False, f"ID 为 {record_id} 的记录不存在，请检查后重试。"

        cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
        conn.commit()
        return True, f"已删除 ID 为 {record_id} 的记录。"
    except sqlite3.Error as e:
        return False, f"删除失败：{e}"
    finally:
        conn.close()


def get_statistics(month: str | None = None) -> pd.DataFrame:
    """
    按分类汇总金额，可选按月筛选。
    返回 DataFrame，包含：分类、笔数、总金额(元)、平均金额(元)。
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        query = """
            SELECT
                category AS "分类",
                COUNT(*) AS "笔数",
                ROUND(SUM(amount), 2) AS "总金额(元)",
                ROUND(AVG(amount), 2) AS "平均金额(元)"
            FROM records
            WHERE 1=1
        """
        params: list = []

        if month:
            query += " AND strftime('%Y-%m', date) = ?"
            params.append(month)

        query += " GROUP BY category ORDER BY SUM(amount) DESC"

        df = pd.read_sql_query(query, conn, params=params)
        return df
    finally:
        conn.close()
