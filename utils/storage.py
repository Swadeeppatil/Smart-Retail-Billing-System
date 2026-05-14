"""Storage management utilities - SQLite based (Replaces JSON)"""

import sqlite3
import csv
import os
import shutil
from typing import List, Dict, Optional, Any
from datetime import datetime
from models.models import Product, BillItem, Invoice, Customer, User, StockMovement

class StorageManager:
    """Manages all local data storage using SQLite Database"""

    def __init__(self, base_path: str = "data"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        
        self.db_path = os.path.join(base_path, "pos_database.sqlite")
        self._initialize_db()

    def get_connection(self):
        """Get a configured SQLite database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _initialize_db(self) -> None:
        """Create tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Products
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id TEXT PRIMARY KEY,
                    name TEXT,
                    category TEXT,
                    cost_price REAL,
                    selling_price REAL,
                    stock_quantity INTEGER,
                    barcode TEXT,
                    expiry_date TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # Database migration: Add expiry_date column if it doesn't exist
            cursor.execute("PRAGMA table_info(products)")
            columns = [info['name'] for info in cursor.fetchall()]
            if 'expiry_date' not in columns:
                cursor.execute("ALTER TABLE products ADD COLUMN expiry_date TEXT DEFAULT ''")
            
            # Invoices
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_id TEXT PRIMARY KEY,
                    customer_name TEXT,
                    customer_phone TEXT,
                    customer_email TEXT,
                    subtotal REAL,
                    discount_percent REAL,
                    discount_amount REAL,
                    gst_percent REAL,
                    gst_amount REAL,
                    grand_total REAL,
                    payment_mode TEXT,
                    created_at TEXT,
                    created_by TEXT,
                    notes TEXT
                )
            ''')
            
            cursor.execute("PRAGMA table_info(invoices)")
            inv_cols = [info['name'] for info in cursor.fetchall()]
            if 'customer_email' not in inv_cols:
                cursor.execute("ALTER TABLE invoices ADD COLUMN customer_email TEXT DEFAULT ''")
            
            # Bill Items
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bill_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id TEXT,
                    product_id TEXT,
                    product_name TEXT,
                    quantity INTEGER,
                    unit_price REAL,
                    discount_percent REAL,
                    line_total REAL,
                    FOREIGN KEY(invoice_id) REFERENCES invoices(invoice_id) ON DELETE CASCADE
                )
            ''')
            
            # Customers
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    name TEXT,
                    phone TEXT,
                    email TEXT,
                    loyalty_points REAL,
                    total_purchases REAL,
                    created_at TEXT
                )
            ''')
            
            # Users
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE,
                    password_hash TEXT,
                    role TEXT,
                    name TEXT,
                    created_at TEXT,
                    is_active INTEGER
                )
            ''')
            
            # Stock Movements
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_movements (
                    movement_id TEXT PRIMARY KEY,
                    product_id TEXT,
                    movement_type TEXT,
                    quantity INTEGER,
                    reference_id TEXT,
                    created_at TEXT,
                    notes TEXT
                )
            ''')
            conn.commit()

    # ========== PRODUCTS ==========
    def add_product(self, product: Product) -> None:
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO products 
                (product_id, name, category, cost_price, selling_price, stock_quantity, barcode, expiry_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product.product_id, product.name, product.category, product.cost_price, 
                product.selling_price, product.stock_quantity, product.barcode, product.expiry_date,
                product.created_at, product.updated_at
            ))

    def get_all_products(self) -> List[Product]:
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM products')
            return [Product(**dict(row)) for row in cursor]

    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM products WHERE product_id = ?', (product_id,))
            row = cursor.fetchone()
            if row:
                return Product(**dict(row))
        return None

    def get_product_by_barcode(self, barcode: str) -> Optional[Product]:
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM products WHERE barcode = ?', (barcode,))
            row = cursor.fetchone()
            if row:
                return Product(**dict(row))
        return None

    def update_product(self, product: Product) -> None:
        product.updated_at = datetime.now().isoformat()
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE products 
                SET name=?, category=?, cost_price=?, selling_price=?, stock_quantity=?, 
                    barcode=?, expiry_date=?, updated_at=?
                WHERE product_id=?
            ''', (
                product.name, product.category, product.cost_price, product.selling_price,
                product.stock_quantity, product.barcode, product.expiry_date, product.updated_at, product.product_id
            ))

    def delete_product(self, product_id: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.execute('DELETE FROM products WHERE product_id=?', (product_id,))
            return cursor.rowcount > 0

    def search_products(self, term: str) -> List[Product]:
        term = f"%{term}%"
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM products WHERE name LIKE ? COLLATE NOCASE', (term,))
            return [Product(**dict(row)) for row in cursor]

    # ========== INVOICES ==========
    def add_invoice(self, invoice: Invoice) -> None:
        with self.get_connection() as conn:
            # Insert invoice
            conn.execute('''
                INSERT INTO invoices
                (invoice_id, customer_name, customer_phone, customer_email, subtotal, discount_percent, 
                 discount_amount, gst_percent, gst_amount, grand_total, payment_mode, 
                 created_at, created_by, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice.invoice_id, invoice.customer_name, invoice.customer_phone, invoice.customer_email, invoice.subtotal,
                invoice.discount_percent, invoice.discount_amount, invoice.gst_percent, invoice.gst_amount,
                invoice.grand_total, invoice.payment_mode, invoice.created_at, invoice.created_by, invoice.notes
            ))
            
            # Insert bill items
            for item in invoice.items:
                conn.execute('''
                    INSERT INTO bill_items
                    (invoice_id, product_id, product_name, quantity, unit_price, discount_percent, line_total)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    invoice.invoice_id, item.product_id, item.product_name, item.quantity,
                    item.unit_price, item.discount_percent, item.line_total
                ))

    def get_all_invoices(self) -> List[Invoice]:
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM invoices ORDER BY created_at DESC')
            invoices = []
            for row in cursor:
                inv_dict = dict(row)
                # Fetch items
                items_cursor = conn.execute('SELECT * FROM bill_items WHERE invoice_id=?', (inv_dict['invoice_id'],))
                items = []
                for item_row in items_cursor:
                    item_dict = dict(item_row)
                    item_dict.pop('id', None)
                    item_dict.pop('invoice_id', None)
                    items.append(item_dict)
                
                inv_dict['items'] = items
                invoices.append(Invoice.from_dict(inv_dict))
            return invoices

    def get_invoice_by_id(self, invoice_id: str) -> Optional[Invoice]:
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM invoices WHERE invoice_id=?', (invoice_id,))
            row = cursor.fetchone()
            if row:
                inv_dict = dict(row)
                items_cursor = conn.execute('SELECT * FROM bill_items WHERE invoice_id=?', (invoice_id,))
                items = []
                for item_row in items_cursor:
                    item_dict = dict(item_row)
                    item_dict.pop('id', None)
                    item_dict.pop('invoice_id', None)
                    items.append(item_dict)
                inv_dict['items'] = items
                return Invoice.from_dict(inv_dict)
        return None

    def get_invoices_by_date(self, date_str: str) -> List[Invoice]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM invoices WHERE created_at LIKE ? ORDER BY created_at DESC", (f"{date_str}%",))
            invoices = []
            for row in cursor:
                inv_dict = dict(row)
                items_cursor = conn.execute('SELECT * FROM bill_items WHERE invoice_id=?', (inv_dict['invoice_id'],))
                items = []
                for item_row in items_cursor:
                    item_dict = dict(item_row)
                    item_dict.pop('id', None)
                    item_dict.pop('invoice_id', None)
                    items.append(item_dict)
                inv_dict['items'] = items
                invoices.append(Invoice.from_dict(inv_dict))
            return invoices

    # ========== CUSTOMERS ==========
    def add_customer(self, customer: Customer) -> None:
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO customers
                (customer_id, name, phone, email, loyalty_points, total_purchases, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                customer.customer_id, customer.name, customer.phone, customer.email,
                customer.loyalty_points, customer.total_purchases, customer.created_at
            ))

    def get_all_customers(self) -> List[Customer]:
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM customers')
            return [Customer(**dict(row)) for row in cursor]

    def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM customers WHERE customer_id=?', (customer_id,))
            row = cursor.fetchone()
            if row:
                return Customer(**dict(row))
        return None

    def get_customer_by_phone(self, phone: str) -> Optional[Customer]:
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM customers WHERE phone=?', (phone,))
            row = cursor.fetchone()
            if row:
                return Customer(**dict(row))
        return None

    def update_customer(self, customer: Customer) -> None:
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE customers
                SET name=?, phone=?, email=?, loyalty_points=?, total_purchases=?
                WHERE customer_id=?
            ''', (
                customer.name, customer.phone, customer.email, customer.loyalty_points,
                customer.total_purchases, customer.customer_id
            ))

    # ========== USERS ==========
    def add_user(self, user: User) -> None:
        with self.get_connection() as conn:
            is_active_int = 1 if user.is_active else 0
            conn.execute('''
                INSERT INTO users
                (user_id, username, password_hash, role, name, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.user_id, user.username, user.password_hash, user.role, 
                user.name, user.created_at, is_active_int
            ))

    def get_all_users(self) -> List[User]:
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM users')
            users = []
            for row in cursor:
                u_dict = dict(row)
                u_dict['is_active'] = bool(u_dict['is_active'])
                users.append(User(**u_dict))
            return users

    def get_user_by_username(self, username: str) -> Optional[User]:
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM users WHERE username=?', (username,))
            row = cursor.fetchone()
            if row:
                u_dict = dict(row)
                u_dict['is_active'] = bool(u_dict['is_active'])
                return User(**u_dict)
        return None

    def update_user(self, user: User) -> None:
        with self.get_connection() as conn:
            is_active_int = 1 if user.is_active else 0
            conn.execute('''
                UPDATE users
                SET username=?, password_hash=?, role=?, name=?, is_active=?
                WHERE user_id=?
            ''', (
                user.username, user.password_hash, user.role, user.name, 
                is_active_int, user.user_id
            ))

    # ========== STOCK MOVEMENTS ==========
    def add_stock_movement(self, movement: StockMovement) -> None:
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO stock_movements
                (movement_id, product_id, movement_type, quantity, reference_id, created_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                movement.movement_id, movement.product_id, movement.movement_type, 
                movement.quantity, movement.reference_id, movement.created_at, movement.notes
            ))

    def get_all_stock_movements(self) -> List[StockMovement]:
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM stock_movements ORDER BY created_at DESC')
            return [StockMovement(**dict(row)) for row in cursor]

    def get_stock_movements_by_product(self, product_id: str) -> List[StockMovement]:
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM stock_movements WHERE product_id=? ORDER BY created_at DESC', (product_id,))
            return [StockMovement(**dict(row)) for row in cursor]

    # ========== UTILITIES ==========
    def export_to_csv(self, file_name: str, data: List[Dict]) -> bool:
        """Export data to CSV"""
        try:
            csv_path = os.path.join(self.base_path, file_name)
            if not data:
                return False
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    def backup_data(self, backup_name: str = None) -> bool:
        """Backup sqlite database"""
        try:
            if backup_name is None:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_dir = os.path.join(self.base_path, "backups", backup_name)
            os.makedirs(backup_dir, exist_ok=True)
            
            db_backup_path = os.path.join(backup_dir, "pos_database.sqlite")
            shutil.copy2(self.db_path, db_backup_path)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False

    def restore_data(self, backup_name: str) -> bool:
        """Restore sqlite database from backup"""
        try:
            backup_dir = os.path.join(self.base_path, "backups", backup_name)
            if not os.path.exists(backup_dir):
                return False
            
            db_backup_path = os.path.join(backup_dir, "pos_database.sqlite")
            if os.path.exists(db_backup_path):
                shutil.copy2(db_backup_path, self.db_path)
                return True
            return False
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
