"""Sales Goal Tracker with daily/weekly/monthly targets"""

import sqlite3
from datetime import datetime, timedelta


class SalesGoalTracker:
    """Track sales targets and progress"""

    def __init__(self, storage, db_path="data/pos_database.sqlite"):
        self.storage = storage
        self.db_path = db_path
        self._ensure_table()

    def _conn(self):
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        return c

    def _ensure_table(self):
        with self._conn() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS sales_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_type TEXT NOT NULL,
                target_amount REAL NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                created_by TEXT
            )''')
            conn.commit()

    def set_goal(self, goal_type, target_amount, created_by="admin"):
        today = datetime.now().date()
        if goal_type == "daily":
            start = end = today.isoformat()
        elif goal_type == "weekly":
            start = (today - timedelta(days=today.weekday())).isoformat()
            end = (today + timedelta(days=6 - today.weekday())).isoformat()
        else:  # monthly
            start = today.replace(day=1).isoformat()
            import calendar
            last_day = calendar.monthrange(today.year, today.month)[1]
            end = today.replace(day=last_day).isoformat()

        with self._conn() as conn:
            conn.execute("DELETE FROM sales_goals WHERE goal_type=? AND start_date=?",
                         (goal_type, start))
            conn.execute('''INSERT INTO sales_goals (goal_type, target_amount, start_date, end_date, created_by)
                VALUES (?, ?, ?, ?, ?)''', (goal_type, target_amount, start, end, created_by))
            conn.commit()

    def get_goal(self, goal_type):
        today = datetime.now().date().isoformat()
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM sales_goals WHERE goal_type=? AND start_date<=? AND end_date>=?",
                (goal_type, today, today)).fetchone()
            return dict(row) if row else None

    def get_progress(self, goal_type):
        goal = self.get_goal(goal_type)
        if not goal:
            return None
        invoices = self.storage.get_all_invoices()
        achieved = sum(i.grand_total for i in invoices
                       if goal["start_date"] <= i.created_at[:10] <= goal["end_date"])
        target = goal["target_amount"]
        pct = min(100, (achieved / target * 100)) if target > 0 else 0
        return {
            "goal_type": goal_type,
            "target": target,
            "achieved": round(achieved, 2),
            "remaining": round(max(0, target - achieved), 2),
            "percentage": round(pct, 1),
            "start": goal["start_date"],
            "end": goal["end_date"],
        }

    def get_streak(self):
        """Calculate how many consecutive days the daily target was met"""
        invoices = self.storage.get_all_invoices()
        today = datetime.now().date()
        streak = 0
        for days_ago in range(1, 60):
            d = (today - timedelta(days=days_ago)).isoformat()
            goal = None
            with self._conn() as conn:
                row = conn.execute(
                    "SELECT target_amount FROM sales_goals WHERE goal_type='daily' AND start_date=?",
                    (d,)).fetchone()
                if row:
                    goal = row[0]
            if goal is None:
                break
            day_sales = sum(i.grand_total for i in invoices if i.created_at[:10] == d)
            if day_sales >= goal:
                streak += 1
            else:
                break
        return streak
