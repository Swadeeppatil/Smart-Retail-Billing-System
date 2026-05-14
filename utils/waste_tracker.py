"""Waste & Spoilage Tracker"""

import sqlite3
from datetime import datetime
from collections import defaultdict


WASTE_REASONS = ["Expired", "Damaged", "Returned by Customer", "Quality Issue", "Spillage", "Other"]


class WasteTracker:
    """Track product waste and spoilage"""

    def __init__(self, db_path="data/pos_database.sqlite"):
        self.db_path = db_path
        self._ensure_table()

    def _conn(self):
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        return c

    def _ensure_table(self):
        with self._conn() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS waste_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL, product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL, reason TEXT,
                cost_per_unit REAL DEFAULT 0, total_loss REAL DEFAULT 0,
                notes TEXT, logged_by TEXT, created_at TEXT
            )''')
            conn.commit()

    def log_waste(self, date, product_name, quantity, reason, cost_per_unit=0, notes="", logged_by="admin"):
        total_loss = cost_per_unit * quantity
        with self._conn() as conn:
            conn.execute('''INSERT INTO waste_log
                (date, product_name, quantity, reason, cost_per_unit, total_loss, notes, logged_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (date, product_name, quantity, reason, cost_per_unit, total_loss, notes, logged_by,
                 datetime.now().isoformat()))
            conn.commit()

    def get_all_waste(self, from_date=None, to_date=None):
        with self._conn() as conn:
            q = "SELECT * FROM waste_log"
            params = []
            if from_date and to_date:
                q += " WHERE date >= ? AND date <= ?"
                params = [from_date, to_date]
            q += " ORDER BY date DESC"
            return [dict(r) for r in conn.execute(q, params)]

    def get_summary(self, from_date=None, to_date=None):
        entries = self.get_all_waste(from_date, to_date)
        total_qty = sum(e['quantity'] for e in entries)
        total_loss = sum(e['total_loss'] for e in entries)
        by_reason = defaultdict(lambda: {"qty": 0, "loss": 0})
        by_product = defaultdict(lambda: {"qty": 0, "loss": 0})
        for e in entries:
            by_reason[e['reason']]["qty"] += e['quantity']
            by_reason[e['reason']]["loss"] += e['total_loss']
            by_product[e['product_name']]["qty"] += e['quantity']
            by_product[e['product_name']]["loss"] += e['total_loss']
        return {
            "total_entries": len(entries), "total_qty": total_qty,
            "total_loss": round(total_loss, 2),
            "by_reason": dict(by_reason),
            "by_product": dict(sorted(by_product.items(), key=lambda x: x[1]["loss"], reverse=True)),
        }

    def delete_entry(self, entry_id):
        with self._conn() as conn:
            conn.execute("DELETE FROM waste_log WHERE id=?", (entry_id,))
            conn.commit()
