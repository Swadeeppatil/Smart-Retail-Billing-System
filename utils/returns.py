"""Return & Refund Management"""
import sqlite3
from datetime import datetime

class ReturnManager:
    def __init__(self, db_path="data/pos_database.sqlite"):
        self.db_path = db_path
        self._ensure()

    def _conn(self):
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        return c

    def _ensure(self):
        with self._conn() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS returns (
                id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_id TEXT,
                product_name TEXT, quantity INTEGER, refund_amount REAL,
                reason TEXT, processed_by TEXT, created_at TEXT)''')
            c.commit()

    def process_return(self, invoice_id, product_name, qty, refund, reason="", by="admin"):
        with self._conn() as c:
            c.execute('INSERT INTO returns VALUES (NULL,?,?,?,?,?,?,?)',
                (invoice_id, product_name, qty, refund, reason, by, datetime.now().isoformat()))
            c.commit()
        return True

    def get_all_returns(self):
        with self._conn() as c:
            return [dict(r) for r in c.execute("SELECT * FROM returns ORDER BY created_at DESC")]

    def get_summary(self):
        rets = self.get_all_returns()
        return {"count": len(rets), "total_items": sum(r['quantity'] for r in rets),
                "total_refund": round(sum(r['refund_amount'] for r in rets), 2)}
