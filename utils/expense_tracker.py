"""Expense Tracker & Profit/Loss Statement Generator"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict


EXPENSE_CATEGORIES = [
    "Rent", "Electricity", "Water", "Salary", "Purchase/Restock",
    "Maintenance", "Transport", "Packaging", "Marketing", "Insurance",
    "Internet/Phone", "Taxes", "Miscellaneous"
]


class ExpenseTracker:
    """Track store expenses and generate P&L statements"""

    def __init__(self, db_path="data/pos_database.sqlite"):
        self.db_path = db_path
        self._ensure_table()

    def _conn(self):
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        return c

    def _ensure_table(self):
        with self._conn() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                amount REAL NOT NULL,
                payment_mode TEXT DEFAULT 'Cash',
                added_by TEXT,
                created_at TEXT
            )''')
            conn.commit()

    def add_expense(self, date, category, amount, description="",
                     payment_mode="Cash", added_by="admin"):
        with self._conn() as conn:
            conn.execute('''INSERT INTO expenses
                (date, category, description, amount, payment_mode, added_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (date, category, description, amount, payment_mode, added_by,
                 datetime.now().isoformat()))
            conn.commit()

    def get_expenses(self, from_date=None, to_date=None) -> List[Dict]:
        with self._conn() as conn:
            q = "SELECT * FROM expenses"
            params = []
            if from_date and to_date:
                q += " WHERE date >= ? AND date <= ?"
                params = [from_date, to_date]
            q += " ORDER BY date DESC"
            cursor = conn.execute(q, params)
            return [dict(r) for r in cursor]

    def get_monthly_expenses(self, year_month) -> List[Dict]:
        """Get expenses for a month (format: YYYY-MM)"""
        with self._conn() as conn:
            cursor = conn.execute(
                "SELECT * FROM expenses WHERE date LIKE ? ORDER BY date",
                (f"{year_month}%",))
            return [dict(r) for r in cursor]

    def get_category_totals(self, from_date=None, to_date=None) -> Dict:
        expenses = self.get_expenses(from_date, to_date)
        totals = {}
        for e in expenses:
            cat = e["category"]
            totals[cat] = totals.get(cat, 0) + e["amount"]
        return totals

    def delete_expense(self, expense_id):
        with self._conn() as conn:
            conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()

    def generate_pnl(self, from_date, to_date, storage) -> Dict:
        """Generate Profit & Loss statement"""
        # Revenue from invoices
        invoices = storage.get_all_invoices()
        filtered_inv = [i for i in invoices
                        if from_date <= i.created_at[:10] <= to_date]
        total_revenue = sum(i.grand_total for i in filtered_inv)
        total_gst = sum(i.gst_amount for i in filtered_inv)

        # COGS (Cost of Goods Sold)
        products = storage.get_all_products()
        cost_map = {p.product_id: p.cost_price for p in products}
        cogs = 0
        for inv in filtered_inv:
            for item in inv.items:
                cogs += cost_map.get(item.product_id, 0) * item.quantity

        gross_profit = total_revenue - total_gst - cogs

        # Operating expenses
        expenses = self.get_expenses(from_date, to_date)
        total_expenses = sum(e["amount"] for e in expenses)
        expense_by_cat = self.get_category_totals(from_date, to_date)

        net_profit = gross_profit - total_expenses
        margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

        return {
            "period": f"{from_date} to {to_date}",
            "total_revenue": round(total_revenue, 2),
            "total_gst": round(total_gst, 2),
            "cogs": round(cogs, 2),
            "gross_profit": round(gross_profit, 2),
            "total_expenses": round(total_expenses, 2),
            "expense_breakdown": expense_by_cat,
            "net_profit": round(net_profit, 2),
            "profit_margin": round(margin, 1),
            "invoice_count": len(filtered_inv),
        }
