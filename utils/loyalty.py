"""Customer Loyalty Points System"""

import sqlite3
from datetime import datetime


LOYALTY_TIERS = {
    "Bronze": (0, 499),
    "Silver": (500, 1999),
    "Gold": (2000, 4999),
    "Platinum": (5000, float('inf')),
}


class LoyaltyManager:
    """Manage customer loyalty points and tiers"""

    POINTS_PER_100 = 1  # 1 point per ₹100 spent
    POINT_VALUE = 1.0   # 1 point = ₹1 redemption

    def __init__(self, db_path="data/pos_database.sqlite"):
        self.db_path = db_path
        self._ensure_table()

    def _conn(self):
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        return c

    def _ensure_table(self):
        with self._conn() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS loyalty_customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                email TEXT,
                points INTEGER DEFAULT 0,
                total_spent REAL DEFAULT 0,
                visit_count INTEGER DEFAULT 0,
                created_at TEXT,
                last_visit TEXT
            )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS loyalty_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_phone TEXT NOT NULL,
                type TEXT NOT NULL,
                points INTEGER NOT NULL,
                invoice_id TEXT,
                description TEXT,
                created_at TEXT
            )''')
            conn.commit()

    def register_customer(self, name, phone, email=""):
        with self._conn() as conn:
            conn.execute('''INSERT OR IGNORE INTO loyalty_customers
                (name, phone, email, points, total_spent, visit_count, created_at, last_visit)
                VALUES (?, ?, ?, 0, 0, 0, ?, ?)''',
                (name, phone, email, datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()

    def find_customer(self, phone):
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM loyalty_customers WHERE phone=?", (phone,)).fetchone()
            return dict(row) if row else None

    def get_all_customers(self):
        with self._conn() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM loyalty_customers ORDER BY points DESC")]

    def earn_points(self, phone, amount, invoice_id=""):
        points = int(amount / 100) * self.POINTS_PER_100
        if points <= 0:
            return 0
        now = datetime.now().isoformat()
        with self._conn() as conn:
            conn.execute("""UPDATE loyalty_customers SET
                points = points + ?, total_spent = total_spent + ?,
                visit_count = visit_count + 1, last_visit = ?
                WHERE phone = ?""", (points, amount, now, phone))
            conn.execute("""INSERT INTO loyalty_transactions
                (customer_phone, type, points, invoice_id, description, created_at)
                VALUES (?, 'EARN', ?, ?, ?, ?)""",
                (phone, points, invoice_id, f"Earned {points} pts on ₹{amount:.0f}", now))
            conn.commit()
        return points

    def redeem_points(self, phone, points, invoice_id=""):
        cust = self.find_customer(phone)
        if not cust or cust['points'] < points:
            return False, 0
        discount = points * self.POINT_VALUE
        now = datetime.now().isoformat()
        with self._conn() as conn:
            conn.execute("UPDATE loyalty_customers SET points = points - ? WHERE phone=?",
                         (points, phone))
            conn.execute("""INSERT INTO loyalty_transactions
                (customer_phone, type, points, invoice_id, description, created_at)
                VALUES (?, 'REDEEM', ?, ?, ?, ?)""",
                (phone, -points, invoice_id, f"Redeemed {points} pts = ₹{discount:.0f} off", now))
            conn.commit()
        return True, discount

    def get_tier(self, phone):
        cust = self.find_customer(phone)
        if not cust:
            return "None"
        pts = cust['points']
        for tier, (low, high) in LOYALTY_TIERS.items():
            if low <= pts <= high:
                return tier
        return "Bronze"

    def get_history(self, phone, limit=20):
        with self._conn() as conn:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM loyalty_transactions WHERE customer_phone=? ORDER BY created_at DESC LIMIT ?",
                (phone, limit))]
