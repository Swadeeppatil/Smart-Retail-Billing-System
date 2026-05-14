"""Billing engine for calculations"""

from typing import List
from models.models import Invoice, BillItem, Product, StockMovement
from utils.storage import StorageManager


class BillingEngine:
    """Handle all billing calculations and operations"""

    def __init__(self, storage: StorageManager):
        self.storage = storage

    def add_item_to_invoice(self, invoice: Invoice, product: Product, quantity: int, discount_percent: float = 0.0) -> bool:
        """Add item to invoice"""
        if product.stock_quantity < quantity:
            return False
        
        item = BillItem(
            product_id=product.product_id,
            product_name=product.name,
            quantity=quantity,
            unit_price=product.selling_price,
            discount_percent=discount_percent
        )
        item.calculate_total()
        invoice.items.append(item)
        return True

    def remove_item_from_invoice(self, invoice: Invoice, index: int) -> bool:
        """Remove item from invoice"""
        if 0 <= index < len(invoice.items):
            invoice.items.pop(index)
            return True
        return False

    def apply_discount(self, invoice: Invoice, discount_percent: float) -> None:
        """Apply discount to entire invoice"""
        invoice.discount_percent = discount_percent
        invoice.calculate_totals()

    def calculate_profit(self, invoice: Invoice) -> float:
        """Calculate profit for an invoice"""
        profit = 0.0
        for item in invoice.items:
            product = self.storage.get_product_by_id(item.product_id)
            if product:
                cost_total = product.cost_price * item.quantity
                profit += item.line_total - cost_total
        return profit

    def finalize_invoice(self, invoice: Invoice) -> bool:
        """Finalize and save invoice, update stock"""
        if not invoice.items:
            return False
        
        invoice.calculate_totals()
        
        # Update stock
        for item in invoice.items:
            product = self.storage.get_product_by_id(item.product_id)
            if product:
                product.stock_quantity -= item.quantity
                self.storage.update_product(product)
                
                # Record stock movement
                movement = StockMovement(
                    product_id=product.product_id,
                    movement_type="SALE",
                    quantity=-item.quantity,
                    reference_id=invoice.invoice_id
                )
                self.storage.add_stock_movement(movement)
        
        # Save invoice
        self.storage.add_invoice(invoice)
        return True

    def get_invoice_summary(self, invoice: Invoice) -> dict:
        """Get invoice summary"""
        invoice.calculate_totals()
        return {
            "invoice_id": invoice.invoice_id,
            "items_count": len(invoice.items),
            "subtotal": invoice.subtotal,
            "discount": invoice.discount_amount,
            "gst": invoice.gst_amount,
            "total": invoice.grand_total,
            "profit": self.calculate_profit(invoice),
            "payment_mode": invoice.payment_mode,
        }
