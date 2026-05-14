"""Reports and Analytics window"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from utils.storage import StorageManager
from utils.billing import BillingEngine


class ReportsWindow:
    """Reports and Analytics UI"""

    def __init__(self, parent, storage: StorageManager, billing: BillingEngine, embed_frame=None):
        self.parent = parent
        self.storage = storage
        self.billing = billing
        
        if embed_frame:
            self.window = embed_frame
        else:
            self.window = tk.Toplevel(parent)
            self.window.title("Reports & Analytics")
            self.window.geometry("1400x850")
            self.window.minsize(1200, 700)
            self.window.configure(bg='#f5f5f5')
        
        self.setup_ui()

    def setup_ui(self):
        """Create reports UI"""
        # Filter frame
        filter_frame = ttk.LabelFrame(self.window, text="Filters", padding="10")
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(filter_frame, text="From Date:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.from_date = ttk.Entry(filter_frame, width=15)
        self.from_date.grid(row=0, column=1, padx=5)
        self.from_date.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))

        ttk.Label(filter_frame, text="To Date:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.to_date = ttk.Entry(filter_frame, width=15)
        self.to_date.grid(row=0, column=3, padx=5)
        self.to_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Button(filter_frame, text="Apply", command=self.apply_filters).grid(row=0, column=4, padx=10)
        ttk.Button(filter_frame, text="Export to CSV", command=self.export_csv).grid(row=0, column=5, padx=5)

        # Notebook
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tabs
        self.sales_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sales_frame, text="Sales Report")

        self.profit_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.profit_frame, text="Profit Analysis")

        self.product_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.product_frame, text="Product Sales")

        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Summary")

        self.apply_filters()

    def apply_filters(self):
        """Apply date filters and refresh reports"""
        try:
            from_date = self.from_date.get()
            to_date = self.to_date.get()
            
            invoices = self.storage.get_all_invoices()
            filtered = [inv for inv in invoices if from_date <= inv.created_at[:10] <= to_date]
            
            self.draw_sales_chart(filtered)
            self.draw_profit_chart(filtered)
            self.draw_product_sales(filtered)
            self.draw_summary(filtered)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def draw_sales_chart(self, invoices):
        """Draw daily sales chart"""
        for widget in self.sales_frame.winfo_children():
            widget.destroy()

        # Calculate daily sales
        daily_sales = {}
        for inv in invoices:
            date = inv.created_at[:10]
            if date not in daily_sales:
                daily_sales[date] = 0
            daily_sales[date] += inv.grand_total

        if not daily_sales:
            ttk.Label(self.sales_frame, text="No data available").pack()
            return

        dates = sorted(daily_sales.keys())
        sales = [daily_sales[d] for d in dates]

        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(dates, sales, marker='o', linewidth=2, color='#1f4788')
        ax.fill_between(range(len(dates)), sales, alpha=0.3, color='#1f4788')
        ax.set_title('Daily Sales Report')
        ax.set_xlabel('Date')
        ax.set_ylabel('Sales (₹)')
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.sales_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def draw_profit_chart(self, invoices):
        """Draw profit analysis"""
        for widget in self.profit_frame.winfo_children():
            widget.destroy()

        # Calculate daily profit
        daily_profit = {}
        for inv in invoices:
            date = inv.created_at[:10]
            profit = self.billing.calculate_profit(inv)
            if date not in daily_profit:
                daily_profit[date] = 0
            daily_profit[date] += profit

        if not daily_profit:
            ttk.Label(self.profit_frame, text="No data available").pack()
            return

        dates = sorted(daily_profit.keys())
        profits = [daily_profit[d] for d in dates]

        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        colors = ['#2ecc71' if p > 0 else '#e74c3c' for p in profits]
        ax.bar(dates, profits, color=colors)
        ax.set_title('Daily Profit Analysis')
        ax.set_xlabel('Date')
        ax.set_ylabel('Profit (₹)')
        ax.tick_params(axis='x', rotation=45)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.profit_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def draw_product_sales(self, invoices):
        """Draw product sales chart"""
        for widget in self.product_frame.winfo_children():
            widget.destroy()

        # Count product sales
        product_sales = {}
        for inv in invoices:
            for item in inv.items:
                if item.product_name not in product_sales:
                    product_sales[item.product_name] = 0
                product_sales[item.product_name] += item.quantity

        if not product_sales:
            ttk.Label(self.product_frame, text="No data available").pack()
            return

        # Top 10 products
        sorted_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:10]
        names = [item[0][:20] for item in sorted_products]
        quantities = [item[1] for item in sorted_products]

        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.barh(names, quantities, color='#3498db')
        ax.set_title('Top 10 Selling Products')
        ax.set_xlabel('Quantity Sold')
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.product_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def draw_summary(self, invoices):
        """Draw summary statistics"""
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.summary_frame, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Calculate stats
        total_revenue = sum(inv.grand_total for inv in invoices)
        total_profit = sum(self.billing.calculate_profit(inv) for inv in invoices)
        total_invoices = len(invoices)
        total_items = sum(len(inv.items) for inv in invoices)
        total_gst = sum(inv.gst_amount for inv in invoices)

        avg_invoice = total_revenue / total_invoices if total_invoices > 0 else 0
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

        # Display stats
        stats = [
            ("Total Revenue", f"₹{total_revenue:.2f}"),
            ("Total Profit", f"₹{total_profit:.2f}"),
            ("Total GST Collected", f"₹{total_gst:.2f}"),
            ("Profit Margin", f"{profit_margin:.2f}%"),
            ("Total Invoices", str(total_invoices)),
            ("Total Items Sold", str(total_items)),
            ("Average Invoice Value", f"₹{avg_invoice:.2f}"),
        ]

        for i, (label, value) in enumerate(stats):
            row = i // 2
            col = i % 2
            label_widget = ttk.Label(frame, text=f"{label}:", font=("Arial", 11, "bold"))
            label_widget.grid(row=row, column=col*2, sticky=tk.W, padx=20, pady=15)
            value_widget = ttk.Label(frame, text=value, font=("Arial", 12), foreground="#2ecc71")
            value_widget.grid(row=row, column=col*2+1, sticky=tk.W, padx=20, pady=15)

    def export_csv(self):
        """Export reports to CSV"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if not file_path:
                return

            from_date = self.from_date.get()
            to_date = self.to_date.get()
            
            invoices = self.storage.get_all_invoices()
            filtered = [inv for inv in invoices if from_date <= inv.created_at[:10] <= to_date]

            data = []
            for inv in filtered:
                for item in inv.items:
                    data.append({
                        "Invoice ID": inv.invoice_id,
                        "Date": inv.created_at,
                        "Customer": inv.customer_name,
                        "Product": item.product_name,
                        "Quantity": item.quantity,
                        "Unit Price": item.unit_price,
                        "Line Total": item.line_total,
                        "Grand Total": inv.grand_total,
                        "Payment Mode": inv.payment_mode,
                    })

            if self.storage.export_to_csv(file_path, data):
                messagebox.showinfo("Success", "Report exported successfully")
            else:
                messagebox.showerror("Error", "Could not export report")
        except Exception as e:
            messagebox.showerror("Error", str(e))
