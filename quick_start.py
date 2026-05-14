#!/usr/bin/env python3
"""
Quick Start Guide for Smart Retail Billing System
"""

import os
import sys
from pathlib import Path

def create_demo_data():
    """Create demo data for testing"""
    from utils.storage import StorageManager
    from utils.auth import AuthManager
    from models.models import Product, Customer
    
    print("Creating demo data...")
    
    storage = StorageManager()
    auth = AuthManager(storage)
    
    # Create demo users
    try:
        auth.create_user("admin", "admin123", "admin", "Administrator")
        auth.create_user("cashier1", "cashier123", "staff", "John Cashier")
        print("✓ Demo users created")
    except:
        print("⚠ Users already exist or error creating users")
    
    # Create demo products
    demo_products = [
        {
            "name": "Laptop",
            "category": "Electronics",
            "cost_price": 25000,
            "selling_price": 35000,
            "stock_quantity": 10,
            "description": "High-performance laptop"
        },
        {
            "name": "Mouse",
            "category": "Electronics",
            "cost_price": 500,
            "selling_price": 999,
            "stock_quantity": 50,
            "description": "Wireless mouse"
        },
        {
            "name": "Keyboard",
            "category": "Electronics",
            "cost_price": 1500,
            "selling_price": 2499,
            "stock_quantity": 30,
            "description": "Mechanical keyboard"
        },
        {
            "name": "Monitor",
            "category": "Electronics",
            "cost_price": 8000,
            "selling_price": 12000,
            "stock_quantity": 15,
            "description": "4K UHD Monitor"
        },
        {
            "name": "USB Cable",
            "category": "Accessories",
            "cost_price": 50,
            "selling_price": 150,
            "stock_quantity": 100,
            "description": "USB-C cable"
        },
    ]
    
    for prod_data in demo_products:
        try:
            product = Product(**prod_data)
            storage.add_product(product)
        except:
            pass
    
    print(f"✓ Created {len(demo_products)} demo products")
    
    # Create demo customers
    demo_customers = [
        {
            "name": "Rajesh Kumar",
            "phone": "9876543210",
            "email": "rajesh@example.com"
        },
        {
            "name": "Priya Singh",
            "phone": "9876543211",
            "email": "priya@example.com"
        },
    ]
    
    for cust_data in demo_customers:
        try:
            customer = Customer(**cust_data)
            storage.add_customer(customer)
        except:
            pass
    
    print(f"✓ Created {len(demo_customers)} demo customers")

def print_header():
    """Print startup header"""
    print("\n" + "=" * 70)
    print("  Smart Retail Billing System - Quick Start")
    print("=" * 70)

def print_instructions():
    """Print quick start instructions"""
    instructions = """
QUICK START GUIDE:

1. DEFAULT CREDENTIALS:
   - Username: admin
   - Password: admin123
   
   ⚠️ IMPORTANT: Change password immediately after first login!

2. FIRST TIME SETUP:
   - Login with admin account
   - Go to Settings → Account → Change Password
   - Create additional users in Settings → User Management
   
3. MAIN FEATURES:

   Dashboard:
   - View today's sales and revenue
   - Check low stock items
   - See top-selling products
   
   Products:
   - Add new products with auto-generated barcodes
   - Set cost price and selling price
   - Track stock quantities
   
   Billing:
   - Create invoices with GST calculation
   - Apply item-wise or invoice-wide discounts
   - Generate PDF invoices
   - Multiple payment modes (Cash, UPI, Card)
   
   Inventory:
   - Real-time stock tracking
   - Stock movement history
   - Low stock alerts
   - Purchase entries
   
   Reports:
   - Daily/Weekly/Monthly sales reports
   - Profit analysis
   - Product sales breakdown
   - Export to CSV
   
   Settings:
   - Manage users and roles
   - Backup and restore data
   - Configure GST and low stock levels

4. SAMPLE DATA:
   Run this command to create demo data for testing:
   
   python quick_start.py --demo
   
5. FILE STRUCTURE:

   data/
   ├── products.json      - Product catalog
   ├── invoices.json      - Invoice records
   ├── customers.json     - Customer info
   ├── users.json         - User accounts
   ├── stock_movements.json
   └── backups/           - Backup files
   
   barcodes/
   └── Generated barcode images
   
   invoices/
   └── Generated PDF invoices

6. DATA BACKUP:
   - Automatic backups are created regularly
   - Manual backup: Settings → Backup & Restore
   - Restore: Settings → Backup & Restore

7. KEYBOARD SHORTCUTS:
   - Login field: Press Enter to submit
   - Most dialogs: Tab to navigate, Enter to submit

8. TROUBLESHOOTING:
   - Cannot login? Check username/password
   - Slow performance? Large dataset? Consider archiving old data
   - Data corrupted? Restore from latest backup
   - Run test_installation.py to verify setup

ENJOY USING SMART RETAIL BILLING SYSTEM! 🎉
"""
    print(instructions)

def main():
    """Main entry point for quick start"""
    print_header()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        create_demo_data()
    else:
        print("\nTo create demo data for testing, run:")
        print("  python quick_start.py --demo\n")
    
    print_instructions()
    print("=" * 70)
    print("\nTo start the application, run:")
    print("  python app.py\n")

if __name__ == "__main__":
    main()
