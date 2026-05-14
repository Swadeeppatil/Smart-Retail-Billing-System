"""Supplier Management & Purchase Order System"""

import sqlite3
from datetime import datetime


class SupplierManager:
    """Manage suppliers and purchase orders"""

    def __init__(self, db_path="data/pos_database.sqlite"):
        self.db_path = db_path
        self._ensure_tables()

    def _conn(self):
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        return c

    def _ensure_tables(self):
        with self._conn() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT, email TEXT, address TEXT,
                products_supplied TEXT, notes TEXT,
                created_at TEXT
            )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS purchase_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER, supplier_name TEXT,
                status TEXT DEFAULT 'Pending',
                items TEXT, total_amount REAL DEFAULT 0,
                order_date TEXT, received_date TEXT,
                notes TEXT
            )''')
            conn.commit()

    def add_supplier(self, name, phone="", email="", address="", products="", notes=""):
        with self._conn() as conn:
            conn.execute('''INSERT INTO suppliers (name, phone, email, address, products_supplied, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (name, phone, email, address, products, notes, datetime.now().isoformat()))
            conn.commit()

    def get_all_suppliers(self):
        with self._conn() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM suppliers ORDER BY name")]

    def delete_supplier(self, sid):
        with self._conn() as conn:
            conn.execute("DELETE FROM suppliers WHERE id=?", (sid,))
            conn.commit()

    def create_purchase_order(self, supplier_id, supplier_name, items_text, total):
        with self._conn() as conn:
            conn.execute('''INSERT INTO purchase_orders
                (supplier_id, supplier_name, status, items, total_amount, order_date)
                VALUES (?, ?, 'Pending', ?, ?, ?)''',
                (supplier_id, supplier_name, items_text, total, datetime.now().isoformat()))
            conn.commit()

    def get_purchase_orders(self, status=None):
        with self._conn() as conn:
            if status:
                return [dict(r) for r in conn.execute(
                    "SELECT * FROM purchase_orders WHERE status=? ORDER BY order_date DESC", (status,))]
            return [dict(r) for r in conn.execute("SELECT * FROM purchase_orders ORDER BY order_date DESC")]

    def update_po_status(self, po_id, status):
        with self._conn() as conn:
            update = "UPDATE purchase_orders SET status=?"
            params = [status]
            if status == "Received":
                update += ", received_date=?"
                params.append(datetime.now().isoformat())
            update += " WHERE id=?"
            params.append(po_id)
            conn.execute(update, params)
            conn.commit()
