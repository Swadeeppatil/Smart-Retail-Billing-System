"""Core data models for Billing System"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict
import uuid


@dataclass
class Product:
    """Product model"""
    product_id: str = field(default_factory=lambda: f"PRD-{uuid.uuid4().hex[:8]}")
    name: str = ""
    category: str = ""
    cost_price: float = 0.0
    selling_price: float = 0.0
    stock_quantity: int = 0
    barcode: str = ""
    expiry_date: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'Product':
        return Product(**data)

    def profit_margin(self) -> float:
        if self.selling_price == 0:
            return 0
        return ((self.selling_price - self.cost_price) / self.selling_price) * 100


@dataclass
class BillItem:
    """Individual item in a bill"""
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    discount_percent: float = 0.0
    line_total: float = field(default=0.0)

    def calculate_total(self) -> float:
        subtotal = self.quantity * self.unit_price
        discount_amount = (subtotal * self.discount_percent) / 100
        self.line_total = subtotal - discount_amount
        return self.line_total

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Invoice:
    """Invoice/Bill model"""
    invoice_id: str = field(default_factory=lambda: f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    items: List[BillItem] = field(default_factory=list)
    customer_name: str = "Walk-in Customer"
    customer_phone: str = ""
    customer_email: str = ""
    subtotal: float = 0.0
    discount_percent: float = 0.0
    discount_amount: float = 0.0
    gst_percent: float = 18.0
    gst_amount: float = 0.0
    grand_total: float = 0.0
    payment_mode: str = "Cash"  # Cash, UPI, Card
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = "System"
    notes: str = ""

    def calculate_totals(self) -> None:
        """Calculate all totals"""
        self.subtotal = sum(item.calculate_total() for item in self.items)
        self.discount_amount = (self.subtotal * self.discount_percent) / 100
        taxable_amount = self.subtotal - self.discount_amount
        self.gst_amount = (taxable_amount * self.gst_percent) / 100
        self.grand_total = taxable_amount + self.gst_amount

    def to_dict(self) -> dict:
        return {
            "invoice_id": self.invoice_id,
            "items": [item.to_dict() for item in self.items],
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "customer_email": self.customer_email,
            "subtotal": self.subtotal,
            "discount_percent": self.discount_percent,
            "discount_amount": self.discount_amount,
            "gst_percent": self.gst_percent,
            "gst_amount": self.gst_amount,
            "grand_total": self.grand_total,
            "payment_mode": self.payment_mode,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: dict) -> 'Invoice':
        items = [BillItem(**item) for item in data.pop("items", [])]
        invoice = Invoice(**data)
        invoice.items = items
        return invoice


@dataclass
class StockMovement:
    """Track stock movements"""
    movement_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str = ""
    movement_type: str = "SALE"  # SALE, PURCHASE, ADJUSTMENT
    quantity: int = 0
    reference_id: str = ""  # invoice_id or purchase_id
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Customer:
    """Customer model"""
    customer_id: str = field(default_factory=lambda: f"CUST-{uuid.uuid4().hex[:6]}")
    name: str = ""
    phone: str = ""
    email: str = ""
    loyalty_points: float = 0.0
    total_purchases: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'Customer':
        return Customer(**data)


@dataclass
class User:
    """User/Employee model"""
    user_id: str = field(default_factory=lambda: f"USR-{uuid.uuid4().hex[:6]}")
    username: str = ""
    password_hash: str = ""
    role: str = "staff"  # admin, staff
    name: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'User':
        return User(**data)


@dataclass
class DashboardStats:
    """Dashboard statistics"""
    total_products: int = 0
    total_sales_today: float = 0.0
    total_invoices_today: int = 0
    monthly_revenue: float = 0.0
    low_stock_items: List[Product] = field(default_factory=list)
    top_selling_products: List[tuple] = field(default_factory=list)  # (product_name, qty)
