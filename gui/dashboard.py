"""Dashboard window"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from utils.storage import StorageManager
from models.models import DashboardStats


class DashboardWindow:
    """Dashboard UI - Main window showing statistics"""

    def __init__(self, parent, storage: StorageManager, user, embed_frame=None):
        self.parent = parent
        self.storage = storage
        self.user = user
        
        if embed_frame:
            self.window = embed_frame
        else:
            self.window = tk.Toplevel(parent)
            self.window.title("Dashboard - Smart Retail Billing")
            self.window.geometry("1000x700")
            self.window.minsize(900, 600)
            try:
                self.window.state("zoomed")
            except Exception:
                pass
        
        self.setup_ui()
        self.refresh_stats()

    def setup_ui(self):
        """Create dashboard UI"""
        # Header
        header_frame = ttk.Frame(self.window)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(header_frame, text="Dashboard", font=("Arial", 18, "bold")).pack(anchor=tk.W)
        ttk.Label(header_frame, text=f"Welcome {self.user.name}", font=("Arial", 10)).pack(anchor=tk.W)

        # Alert Frame
        self.alert_frame = ttk.Frame(self.window)
        self.alert_frame.pack(fill=tk.X, padx=10, pady=5)
        self.expiry_alert_label = tk.Label(self.alert_frame, text="", fg="white", bg="red", font=("Arial", 11, "bold"))

        # Stats Frame
        stats_frame = ttk.LabelFrame(self.window, text="Quick Stats", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        # Stats grid
        self.total_products_label = ttk.Label(stats_frame, text="Total Products: 0", font=("Arial", 11))
        self.total_products_label.grid(row=0, column=0, padx=20, pady=10, sticky=tk.W)

        self.total_sales_label = ttk.Label(stats_frame, text="Sales Today: ₹0.00", font=("Arial", 11))
        self.total_sales_label.grid(row=0, column=1, padx=20, pady=10, sticky=tk.W)

        self.invoices_today_label = ttk.Label(stats_frame, text="Invoices Today: 0", font=("Arial", 11))
        self.invoices_today_label.grid(row=0, column=2, padx=20, pady=10, sticky=tk.W)

        self.monthly_revenue_label = ttk.Label(stats_frame, text="Monthly Revenue: ₹0.00", font=("Arial", 11))
        self.monthly_revenue_label.grid(row=1, column=0, padx=20, pady=10, sticky=tk.W)

        # Charts Frame
        charts_frame = ttk.LabelFrame(self.window, text="Analytics", padding="10")
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(charts_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Chart tabs
        self.sales_chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sales_chart_frame, text="Sales Chart")

        self.top_products_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.top_products_frame, text="Top Products")

        self.low_stock_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.low_stock_frame, text="Low Stock")

        self.expiring_items_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.expiring_items_frame, text="Expiring Items (30 Days)")

        self.category_pie_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.category_pie_frame, text="📊 Category Distribution")

        self.revenue_profit_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.revenue_profit_frame, text="💰 Revenue vs Profit")

        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Refresh", command=self.refresh_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)

    def refresh_stats(self):
        """Refresh dashboard statistics"""
        self.calculate_stats()
        self.update_charts()

    def calculate_stats(self):
        """Calculate dashboard statistics"""
        products = self.storage.get_all_products()
        invoices = self.storage.get_all_invoices()
        
        today = datetime.now().strftime("%Y-%m-%d")
        today_invoices = self.storage.get_invoices_by_date(today)
        
        # Total products
        total_products = len(products)
        self.total_products_label.config(text=f"Total Products: {total_products}")

        # Sales today
        sales_today = sum(inv.grand_total for inv in today_invoices)
        self.total_sales_label.config(text=f"Sales Today: ₹{sales_today:.2f}")

        # Invoices today
        invoices_today = len(today_invoices)
        self.invoices_today_label.config(text=f"Invoices Today: {invoices_today}")

        # Monthly revenue
        month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        monthly_invoices = [inv for inv in invoices if inv.created_at >= month_start]
        monthly_revenue = sum(inv.grand_total for inv in monthly_invoices)
        self.monthly_revenue_label.config(text=f"Monthly Revenue: ₹{monthly_revenue:.2f}")

    def update_charts(self):
        """Update dashboard charts"""
        self.draw_sales_chart()
        self.draw_top_products_chart()
        self.draw_low_stock_chart()
        self.draw_expiring_items()
        self.draw_category_pie()
        self.draw_revenue_profit()

    def draw_sales_chart(self):
        """Draw sales chart for last 7 days"""
        # Clear previous
        for widget in self.sales_chart_frame.winfo_children():
            widget.destroy()

        invoices = self.storage.get_all_invoices()
        
        # Get last 7 days sales
        daily_sales = {}
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            daily_sales[date] = 0

        for inv in invoices:
            date = inv.created_at[:10]
            if date in daily_sales:
                daily_sales[date] += inv.grand_total

        # Plot
        dates = sorted(daily_sales.keys())
        sales = [daily_sales[date] for date in dates]

        fig = Figure(figsize=(8, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(dates, sales, color='#1f4788')
        ax.set_title('Sales (Last 7 Days)')
        ax.set_xlabel('Date')
        ax.set_ylabel('Amount (₹)')
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.sales_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def draw_top_products_chart(self):
        """Draw top selling products"""
        for widget in self.top_products_frame.winfo_children():
            widget.destroy()

        invoices = self.storage.get_all_invoices()
        
        # Count sales
        product_sales = {}
        for inv in invoices:
            for item in inv.items:
                if item.product_id not in product_sales:
                    product_sales[item.product_id] = {"name": item.product_name, "qty": 0}
                product_sales[item.product_id]["qty"] += item.quantity

        # Sort by quantity
        sorted_products = sorted(product_sales.items(), key=lambda x: x[1]["qty"], reverse=True)[:5]

        if not sorted_products:
            ttk.Label(self.top_products_frame, text="No sales data").pack()
            return

        names = [item[1]["name"] for item in sorted_products]
        quantities = [item[1]["qty"] for item in sorted_products]

        fig = Figure(figsize=(8, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.barh(names, quantities, color='#2ecc71')
        ax.set_title('Top Selling Products')
        ax.set_xlabel('Quantity Sold')
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.top_products_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def draw_low_stock_chart(self):
        """Draw low stock items"""
        for widget in self.low_stock_frame.winfo_children():
            widget.destroy()

        products = self.storage.get_all_products()
        low_stock = [p for p in products if p.stock_quantity <= 10]

        if not low_stock:
            ttk.Label(self.low_stock_frame, text="No low stock items").pack(pady=20)
            return

        # Create treeview
        tree_frame = ttk.Frame(self.low_stock_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(tree_frame, columns=("Name", "Stock", "Category"), height=7)
        tree.column("#0", width=100)
        tree.column("Name", width=200)
        tree.column("Stock", width=80)
        tree.column("Category", width=150)

        tree.heading("#0", text="ID")
        tree.heading("Name", text="Product Name")
        tree.heading("Stock", text="Stock")
        tree.heading("Category", text="Category")

        for product in low_stock:
            tree.insert("", tk.END, text=product.product_id[:8], 
                       values=(product.name, product.stock_quantity, product.category))

        tree.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscroll=scrollbar.set)

    def draw_expiring_items(self):
        """Draw items expiring soon or already expired"""
        for widget in self.expiring_items_frame.winfo_children():
            widget.destroy()

        products = self.storage.get_all_products()
        expiring = []
        today = datetime.now().date()
        limit_date = today + timedelta(days=30)

        for p in products:
            if hasattr(p, 'expiry_date') and p.expiry_date:
                for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d'):
                    try:
                        exp_date = datetime.strptime(p.expiry_date.strip(), fmt).date()
                        if exp_date <= limit_date:
                            expiring.append((p, exp_date))
                        break # Successfully parsed
                    except ValueError:
                        continue

        # Sort by expiry date closest first
        expiring.sort(key=lambda x: x[1])

        if not expiring:
            self.expiry_alert_label.pack_forget()
            ttk.Label(self.expiring_items_frame, text="No items expiring soon.").pack(pady=20)
            return
        
        expired_count = sum(1 for p, d in expiring if d < today)
        expiring_count = len(expiring) - expired_count
        
        alert_text = f" ⚠ WARNING: {expired_count} Items Expired and {expiring_count} Expiring within 30 days! Check the 'Expiring Items' Tab. "
        self.expiry_alert_label.config(text=alert_text)
        self.expiry_alert_label.pack(fill=tk.X, ipady=8)

        # Create treeview
        tree_frame = ttk.Frame(self.expiring_items_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(tree_frame, columns=("Name", "Stock", "Expiry"), height=7)
        tree.column("#0", width=100)
        tree.column("Name", width=200)
        tree.column("Stock", width=80)
        tree.column("Expiry", width=150)

        tree.heading("#0", text="Product ID")
        tree.heading("Name", text="Product Name")
        tree.heading("Stock", text="Stock")
        tree.heading("Expiry", text="Expiry Date")

        for product, d in expiring:
            tag = "expired" if d < today else "warning"
            tree.insert("", tk.END, text=product.product_id[:8], 
                       values=(product.name, product.stock_quantity, product.expiry_date), tags=(tag,))

        tree.tag_configure("expired", background="#ffcccc", foreground="black")
        tree.tag_configure("warning", background="#fff3cd", foreground="black")

        tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscroll=scrollbar.set)

    def draw_category_pie(self):
        """Draw category-wise product distribution pie chart"""
        for widget in self.category_pie_frame.winfo_children():
            widget.destroy()

        products = self.storage.get_all_products()
        if not products:
            ttk.Label(self.category_pie_frame, text="No products available").pack(pady=20)
            return

        # Count products per category
        cat_counts = {}
        for p in products:
            cat = p.category if p.category else "Uncategorized"
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        labels = list(cat_counts.keys())
        sizes = list(cat_counts.values())
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6',
                  '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b',
                  '#8e44ad', '#27ae60', '#d35400', '#2980b9', '#7f8c8d']
        # Extend colors if more categories
        while len(colors) < len(labels):
            colors += colors

        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct='%1.1f%%',
            colors=colors[:len(labels)], startangle=140,
            textprops={'fontsize': 8}
        )
        ax.set_title('Product Distribution by Category', fontsize=12, fontweight='bold')
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.category_pie_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def draw_revenue_profit(self):
        """Draw revenue vs profit comparison chart for last 7 days"""
        for widget in self.revenue_profit_frame.winfo_children():
            widget.destroy()

        invoices = self.storage.get_all_invoices()

        # Get last 7 days
        daily_data = {}
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            daily_data[date] = {"revenue": 0, "cost": 0}

        products = self.storage.get_all_products()
        product_costs = {p.product_id: p.cost_price for p in products}

        for inv in invoices:
            date = inv.created_at[:10]
            if date in daily_data:
                daily_data[date]["revenue"] += inv.grand_total
                for item in inv.items:
                    cost_price = product_costs.get(item.product_id, 0)
                    daily_data[date]["cost"] += cost_price * item.quantity

        dates = sorted(daily_data.keys())
        revenues = [daily_data[d]["revenue"] for d in dates]
        profits = [daily_data[d]["revenue"] - daily_data[d]["cost"] for d in dates]

        if not any(revenues):
            ttk.Label(self.revenue_profit_frame, text="No sales data for last 7 days").pack(pady=20)
            return

        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)

        import numpy as np
        x = np.arange(len(dates))
        width = 0.35
        bars1 = ax.bar(x - width/2, revenues, width, label='Revenue', color='#3498db')
        bars2 = ax.bar(x + width/2, profits, width, label='Profit', color='#2ecc71')

        ax.set_title('Revenue vs Profit (Last 7 Days)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Amount (₹)')
        ax.set_xticks(x)
        ax.set_xticklabels([d[5:] for d in dates], rotation=45)
        ax.legend()
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.revenue_profit_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
