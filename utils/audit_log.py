"""Audit/Activity Log module for Smart Retail Billing System

Tracks all user actions with timestamps for accountability and review.
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional


class AuditLogger:
    """Logs all system actions for audit trail"""

    def __init__(self, db_path: str = "data/pos_database.sqlite"):
        self.db_path = db_path
        self._ensure_table()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_table(self):
        """Create the audit_log table if it doesn't exist"""
        with self._get_conn() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user TEXT NOT NULL,
                    action TEXT NOT NULL,
                    category TEXT NOT NULL,
                    details TEXT,
                    ip_info TEXT
                )
            ''')
            conn.commit()

    def log(self, user: str, action: str, category: str, details: str = ""):
        """Log an action
        
        Args:
            user: Username who performed the action
            action: What was done (e.g., "Added Product", "Deleted Invoice")
            category: Category of action (LOGIN, PRODUCT, BILLING, SETTINGS, SYSTEM)
            details: Additional details
        """
        with self._get_conn() as conn:
            conn.execute('''
                INSERT INTO audit_log (timestamp, user, action, category, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                user,
                action,
                category,
                details
            ))
            conn.commit()

    def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent audit log entries"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                'SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?', (limit,)
            )
            return [dict(row) for row in cursor]

    def get_logs_by_user(self, user: str, limit: int = 50) -> List[Dict]:
        """Get logs for a specific user"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                'SELECT * FROM audit_log WHERE user = ? ORDER BY timestamp DESC LIMIT ?',
                (user, limit)
            )
            return [dict(row) for row in cursor]

    def get_logs_by_category(self, category: str, limit: int = 50) -> List[Dict]:
        """Get logs for a specific category"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                'SELECT * FROM audit_log WHERE category = ? ORDER BY timestamp DESC LIMIT ?',
                (category, limit)
            )
            return [dict(row) for row in cursor]

    def get_logs_by_date(self, date_str: str) -> List[Dict]:
        """Get logs for a specific date (YYYY-MM-DD)"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                'SELECT * FROM audit_log WHERE timestamp LIKE ? ORDER BY timestamp DESC',
                (f"{date_str}%",)
            )
            return [dict(row) for row in cursor]

    def get_login_history(self, limit: int = 20) -> List[Dict]:
        """Get login/logout history"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                'SELECT * FROM audit_log WHERE category = "LOGIN" ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            )
            return [dict(row) for row in cursor]

    def clear_old_logs(self, days: int = 90):
        """Clear logs older than specified days"""
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        with self._get_conn() as conn:
            conn.execute('DELETE FROM audit_log WHERE timestamp < ?', (cutoff,))
            conn.commit()
