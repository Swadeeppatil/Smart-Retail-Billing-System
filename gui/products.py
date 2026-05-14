"""Product management window"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import calendar
from utils.storage import StorageManager
from utils.barcode import BarcodeManager
from models.models import Product

# Predefined category list for dropdown
PRODUCT_CATEGORIES = [
    "Groceries",
    "Dairy Products",
    "Beverages",
    "Snacks & Chips",
    "Fruits & Vegetables",
    "Bakery",
    "Frozen Foods",
    "Personal Care",
    "Household Items",
    "Stationery",
    "Electronics",
    "Clothing",
    "Medicines",
    "Confectionery",
    "Spices & Masala",
    "Oil & Ghee",
    "Rice & Flour",
    "Pulses & Lentils",
    "Canned Foods",
    "Baby Products",
    "Pet Supplies",
    "Other",
]


def get_expiry_status(expiry_date_str):
    if not expiry_date_str: return ""
    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d'):
        try:
            exp_date = datetime.strptime(expiry_date_str.strip(), fmt).date()
            today = datetime.now().date()
            if exp_date < today:
                return "expired"
            elif exp_date <= today + timedelta(days=30):
                return "expiring"
            return ""
        except ValueError:
            continue
    return ""


# ─── Calendar Date Picker Widget ───────────────────────────────────────────
class CalendarPopup:
    """A simple calendar date-picker popup for Tkinter"""

    def __init__(self, parent, callback, min_date=None):
        """
        parent   – parent widget
        callback – called with selected date string (YYYY-MM-DD)
        min_date – datetime.date; dates before this are disabled
        """
        self.callback = callback
        self.min_date = min_date

        self.top = tk.Toplevel(parent)
        self.top.title("Select Date")
        self.top.geometry("320x340")
        self.top.resizable(False, False)
        self.top.configure(bg="#ffffff")
        self.top.grab_set()

        today = datetime.now().date()
        self.year = today.year
        self.month = today.month

        self._build_ui()

    # ── UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Navigation header
        nav = tk.Frame(self.top, bg="#007acc")
        nav.pack(fill=tk.X)

        tk.Button(nav, text="◀", font=("Arial", 12, "bold"), bg="#007acc",
                  fg="white", bd=0, command=self._prev_month).pack(side=tk.LEFT, padx=10, pady=6)
        self.header_lbl = tk.Label(nav, text="", font=("Arial", 13, "bold"),
                                   bg="#007acc", fg="white")
        self.header_lbl.pack(side=tk.LEFT, expand=True)
        tk.Button(nav, text="▶", font=("Arial", 12, "bold"), bg="#007acc",
                  fg="white", bd=0, command=self._next_month).pack(side=tk.RIGHT, padx=10, pady=6)

        # Day-of-week header
        dow_frame = tk.Frame(self.top, bg="#e8f0fe")
        dow_frame.pack(fill=tk.X)
        for d in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"):
            tk.Label(dow_frame, text=d, width=4, font=("Arial", 9, "bold"),
                     bg="#e8f0fe", fg="#333").pack(side=tk.LEFT, expand=True)

        # Day grid
        self.grid_frame = tk.Frame(self.top, bg="#ffffff")
        self.grid_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Today button
        tk.Button(self.top, text="Today", font=("Arial", 10, "bold"),
                  bg="#27ae60", fg="white", bd=0, padx=15, pady=4,
                  command=self._select_today).pack(pady=6)

        self._draw_month()

    def _draw_month(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        self.header_lbl.config(text=f"{calendar.month_name[self.month]}  {self.year}")

        cal = calendar.monthcalendar(self.year, self.month)
        today = datetime.now().date()

        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day == 0:
                    tk.Label(self.grid_frame, text="", width=4, height=2,
                             bg="#ffffff").grid(row=r, column=c)
                    continue

                d = datetime(self.year, self.month, day).date()
                is_past = self.min_date and d < self.min_date
                is_today = d == today

                if is_today:
                    bg, fg = "#007acc", "white"
                elif is_past:
                    bg, fg = "#f0f0f0", "#bbbbbb"
                elif c == 6:  # Sunday
                    bg, fg = "#fff0f0", "#cc3333"
                else:
                    bg, fg = "#ffffff", "#333333"

                btn = tk.Button(
                    self.grid_frame, text=str(day), width=4, height=2,
                    font=("Arial", 10), bg=bg, fg=fg, bd=1, relief="flat",
                    activebackground="#cce5ff",
                    command=lambda dd=d, past=is_past: self._on_day(dd, past)
                )
                btn.grid(row=r, column=c, padx=1, pady=1)

    def _on_day(self, date_obj, is_past):
        if is_past:
            messagebox.showwarning(
                "Invalid Date",
                f"❌ You cannot select a past date!\n\n"
                f"Selected: {date_obj.strftime('%d-%m-%Y')}\n"
                f"Today:      {datetime.now().strftime('%d-%m-%Y')}\n\n"
                f"Please select today's date or a future date.",
                parent=self.top)
            return
        self.callback(date_obj.strftime("%Y-%m-%d"))
        self.top.destroy()

    def _prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self._draw_month()

    def _next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self._draw_month()

    def _select_today(self):
        today = datetime.now().date()
        self.callback(today.strftime("%Y-%m-%d"))
        self.top.destroy()


# ─── Product Window ─────────────────────────────────────────────────────────
class ProductWindow:
    """Product management UI"""

    def __init__(self, parent, storage: StorageManager, barcode_mgr: BarcodeManager, embed_frame=None):
        self.parent = parent
        self.storage = storage
        self.barcode_mgr = barcode_mgr
        
        if embed_frame:
            self.window = embed_frame
        else:
            self.window = tk.Toplevel(parent)
            self.window.title("Product Management")
            self.window.geometry("1000x700")
            self.window.minsize(900, 600)
            try:
                self.window.state("zoomed")
            except Exception:
                pass
            self.window.configure(bg='#f5f5f5')
        
        self.setup_ui()
        self.refresh_products()

    def setup_ui(self):
        """Create product management UI"""
        # ── Advanced Search & Filter Bar ──────────────────────────────
        search_frame = ttk.LabelFrame(self.window, text="🔍 Search & Filters", padding="5")
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        # Row 1: Text search
        row1 = ttk.Frame(search_frame)
        row1.pack(fill=tk.X, pady=3)

        ttk.Label(row1, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(row1, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.apply_filters())

        ttk.Button(row1, text="🔍 Search", command=self.apply_filters).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1, text="🔄 Reset", command=self.reset_filters).pack(side=tk.LEFT, padx=5)

        # Row 2: Category, Stock, Expiry filters
        row2 = ttk.Frame(search_frame)
        row2.pack(fill=tk.X, pady=3)

        ttk.Label(row2, text="Category:").pack(side=tk.LEFT, padx=5)
        self.filter_category_var = tk.StringVar(value="All")
        cat_values = ["All"] + PRODUCT_CATEGORIES
        ttk.Combobox(row2, textvariable=self.filter_category_var, values=cat_values,
                     state="readonly", width=15).pack(side=tk.LEFT, padx=5)

        ttk.Label(row2, text="Stock:").pack(side=tk.LEFT, padx=5)
        self.filter_stock_var = tk.StringVar(value="All")
        ttk.Combobox(row2, textvariable=self.filter_stock_var,
                     values=["All", "Low Stock (≤10)", "Out of Stock", "In Stock"],
                     state="readonly", width=15).pack(side=tk.LEFT, padx=5)

        ttk.Label(row2, text="Expiry:").pack(side=tk.LEFT, padx=5)
        self.filter_expiry_var = tk.StringVar(value="All")
        ttk.Combobox(row2, textvariable=self.filter_expiry_var,
                     values=["All", "Expired", "Expiring (30 days)", "Valid"],
                     state="readonly", width=16).pack(side=tk.LEFT, padx=5)

        ttk.Button(row2, text="Apply Filters", command=self.apply_filters).pack(side=tk.LEFT, padx=10)

        # Product count label
        self.count_label = ttk.Label(row2, text="", font=("Arial", 9, "bold"))
        self.count_label.pack(side=tk.RIGHT, padx=10)


        # Products treeview
        tree_frame = ttk.Frame(self.window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(tree_frame, columns=(
            "Category", "Cost", "Selling", "Stock", "Barcode", "Expiry"
        ), yscrollcommand=vsb.set, xscrollcommand=hsb.set, height=8)

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        self.tree.column("#0", width=150, minwidth=150)
        self.tree.column("Category", width=100, minwidth=100)
        self.tree.column("Cost", width=80, minwidth=80)
        self.tree.column("Selling", width=80, minwidth=80)
        self.tree.column("Stock", width=80, minwidth=80)
        self.tree.column("Barcode", width=120, minwidth=120)
        self.tree.column("Expiry", width=100, minwidth=100)

        self.tree.heading("#0", text="Product Name")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Cost", text="Cost Price")
        self.tree.heading("Selling", text="Selling Price")
        self.tree.heading("Stock", text="Stock")
        self.tree.heading("Barcode", text="Barcode")
        self.tree.heading("Expiry", text="Expiry")

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Right-click menu
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Button-1>", self.on_tree_click)

        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Add Product", command=self.add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit", command=self.edit_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)

        self.selected_item = None

    def on_tree_click(self, event):
        """Handle tree click"""
        item = self.tree.selection()
        if item:
            self.selected_item = item[0]

    def refresh_products(self):
        """Refresh product list (shows all, respecting filters)"""
        self.apply_filters()

    def apply_filters(self):
        """Apply all active filters and display matching products"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        term = self.search_entry.get().strip().lower()
        cat_filter = self.filter_category_var.get()
        stock_filter = self.filter_stock_var.get()
        expiry_filter = self.filter_expiry_var.get()

        products = self.storage.get_all_products()
        filtered = []

        for p in products:
            # Text search filter
            if term and term not in p.name.lower() and term not in p.barcode.lower():
                continue
            # Category filter
            if cat_filter != "All" and p.category != cat_filter:
                continue
            # Stock filter
            if stock_filter == "Low Stock (≤10)" and p.stock_quantity > 10:
                continue
            if stock_filter == "Out of Stock" and p.stock_quantity > 0:
                continue
            if stock_filter == "In Stock" and p.stock_quantity <= 0:
                continue
            # Expiry filter
            status = get_expiry_status(p.expiry_date)
            if expiry_filter == "Expired" and status != "expired":
                continue
            if expiry_filter == "Expiring (30 days)" and status != "expiring":
                continue
            if expiry_filter == "Valid" and status in ("expired", "expiring"):
                continue

            filtered.append(p)

        self._display_products(filtered)

    def _display_products(self, products):
        """Display a list of products in the treeview"""
        for product in products:
            status = get_expiry_status(product.expiry_date)
            if status == "expired":
                tag = "expired"
            elif status == "expiring":
                tag = "expiring"
            else:
                tag = "low_stock" if product.stock_quantity <= 10 else ""
                
            self.tree.insert("", tk.END, text=product.name, values=(
                product.category,
                f"₹{product.cost_price:.2f}",
                f"₹{product.selling_price:.2f}",
                product.stock_quantity,
                product.barcode,
                product.expiry_date if product.expiry_date else "-"
            ), tags=(tag,))

        self.tree.tag_configure("low_stock", foreground="red")
        self.tree.tag_configure("expired", background="#ffcccc", foreground="black")
        self.tree.tag_configure("expiring", background="#fff3cd", foreground="black")

        # Update count label
        self.count_label.config(text=f"Showing {len(products)} products")

    def reset_filters(self):
        """Reset all filters to defaults"""
        self.search_entry.delete(0, tk.END)
        self.filter_category_var.set("All")
        self.filter_stock_var.set("All")
        self.filter_expiry_var.set("All")
        self.apply_filters()

    def search_products(self):
        """Search products (delegates to apply_filters)"""
        self.apply_filters()


    def add_product(self):
        """Show add product dialog"""
        dialog = ProductDialog(self.window, self.storage, self.barcode_mgr)
        self.window.wait_window(dialog.dialog)
        self.refresh_products()

    def edit_product(self):
        """Edit selected product"""
        if not self.selected_item:
            messagebox.showwarning("Warning", "Please select a product")
            return

        # Get product from tree
        product_name = self.tree.item(self.selected_item, "text")
        products = self.storage.get_all_products()
        product = None
        for p in products:
            if p.name == product_name:
                product = p
                break

        if product:
            dialog = ProductDialog(self.window, self.storage, self.barcode_mgr, product)
            self.window.wait_window(dialog.dialog)
            self.refresh_products()

    def delete_product(self):
        """Delete selected product"""
        if not self.selected_item:
            messagebox.showwarning("Warning", "Please select a product")
            return

        if messagebox.askyesno("Confirm", "Delete this product?"):
            product_name = self.tree.item(self.selected_item, "text")
            products = self.storage.get_all_products()
            for p in products:
                if p.name == product_name:
                    self.storage.delete_product(p.product_id)
                    self.refresh_products()
                    messagebox.showinfo("Success", "Product deleted")
                    break

    def show_context_menu(self, event):
        """Show context menu"""
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="Edit", command=self.edit_product)
        menu.add_command(label="Delete", command=self.delete_product)
        menu.post(event.x_root, event.y_root)


class ProductDialog:
    """Product add/edit dialog"""

    def __init__(self, parent, storage: StorageManager, barcode_mgr: BarcodeManager, product: Product = None):
        self.storage = storage
        self.barcode_mgr = barcode_mgr
        self.product = product
        self.generated_barcode = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Product" if not product else "Edit Product")
        self.dialog.geometry("450x550")
        self.dialog.resizable(False, False)

        self.setup_ui()

        if product:
            self.populate_fields(product)

    def setup_ui(self):
        """Create dialog UI"""
        frame = ttk.Frame(self.dialog, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)

        # Product Name
        ttk.Label(frame, text="Product Name:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.name_entry = ttk.Entry(frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=10)

        # Category – dropdown list
        ttk.Label(frame, text="Category:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(frame, textvariable=self.category_var,
                                            values=PRODUCT_CATEGORIES, width=28, state="readonly")
        self.category_combo.grid(row=1, column=1, pady=10)
        self.category_combo.set("Groceries")

        # Cost Price
        ttk.Label(frame, text="Cost Price (₹):").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.cost_entry = ttk.Entry(frame, width=30)
        self.cost_entry.grid(row=2, column=1, pady=10)

        # Selling Price
        ttk.Label(frame, text="Selling Price (₹):").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.selling_entry = ttk.Entry(frame, width=30)
        self.selling_entry.grid(row=3, column=1, pady=10)

        # Stock Quantity
        ttk.Label(frame, text="Stock Quantity:").grid(row=4, column=0, sticky=tk.W, pady=10)
        self.stock_entry = ttk.Entry(frame, width=30)
        self.stock_entry.grid(row=4, column=1, pady=10)

        # Barcode
        ttk.Label(frame, text="Barcode:").grid(row=5, column=0, sticky=tk.W, pady=10)
        barcode_frame = ttk.Frame(frame)
        barcode_frame.grid(row=5, column=1, pady=10)
        self.barcode_entry = ttk.Entry(barcode_frame, width=20)
        self.barcode_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(barcode_frame, text="Generate", command=self.generate_barcode).pack(side=tk.LEFT)

        # Expiry Date – calendar picker
        ttk.Label(frame, text="Expiry Date:").grid(row=6, column=0, sticky=tk.W, pady=10)
        expiry_frame = ttk.Frame(frame)
        expiry_frame.grid(row=6, column=1, pady=10)
        self.expiry_entry = ttk.Entry(expiry_frame, width=20, state="readonly")
        self.expiry_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(expiry_frame, text="📅 Pick", command=self.open_calendar).pack(side=tk.LEFT)
        ttk.Button(expiry_frame, text="✕", width=3, command=self.clear_expiry).pack(side=tk.LEFT, padx=2)

        # Expiry status label
        self.expiry_status_lbl = ttk.Label(frame, text="", font=("Arial", 8))
        self.expiry_status_lbl.grid(row=7, column=1, sticky=tk.W)

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def open_calendar(self):
        """Open the calendar popup for expiry date selection"""
        today = datetime.now().date()
        CalendarPopup(self.dialog, self._on_date_selected, min_date=today)

    def _on_date_selected(self, date_str):
        """Callback when a date is selected from calendar"""
        self.expiry_entry.configure(state="normal")
        self.expiry_entry.delete(0, tk.END)
        self.expiry_entry.insert(0, date_str)
        self.expiry_entry.configure(state="readonly")
        # Show status
        self.expiry_status_lbl.configure(text=f"✅ Expiry set: {date_str}", foreground="#27ae60")

    def clear_expiry(self):
        """Clear the expiry date field"""
        self.expiry_entry.configure(state="normal")
        self.expiry_entry.delete(0, tk.END)
        self.expiry_entry.configure(state="readonly")
        self.expiry_status_lbl.configure(text="No expiry date set", foreground="#999999")

    def populate_fields(self, product: Product):
        """Populate fields with existing data"""
        self.name_entry.insert(0, product.name)
        # Set category in combo
        if product.category in PRODUCT_CATEGORIES:
            self.category_combo.set(product.category)
        else:
            # If old category isn't in list, add it temporarily
            vals = list(PRODUCT_CATEGORIES) + [product.category]
            self.category_combo['values'] = vals
            self.category_combo.set(product.category)
        self.cost_entry.insert(0, str(product.cost_price))
        self.selling_entry.insert(0, str(product.selling_price))
        self.stock_entry.insert(0, str(product.stock_quantity))
        self.barcode_entry.insert(0, product.barcode)
        if hasattr(product, 'expiry_date') and product.expiry_date:
            self.expiry_entry.configure(state="normal")
            self.expiry_entry.insert(0, product.expiry_date)
            self.expiry_entry.configure(state="readonly")

    def generate_barcode(self):
        """Generate barcode"""
        if self.product:
            barcode_num = BarcodeManager.generate_unique_barcode(self.product.product_id)
        else:
            import uuid
            barcode_num = BarcodeManager.generate_unique_barcode(str(uuid.uuid4()))
        self.barcode_entry.delete(0, tk.END)
        self.barcode_entry.insert(0, barcode_num)

    def save(self):
        """Save product"""
        try:
            name = self.name_entry.get().strip()
            category = self.category_var.get().strip()
            cost = float(self.cost_entry.get())
            selling = float(self.selling_entry.get())
            stock = int(self.stock_entry.get())
            barcode = self.barcode_entry.get().strip()
            expiry_date = self.expiry_entry.get().strip()

            if not name or not category or cost < 0 or selling < 0 or stock < 0:
                messagebox.showerror("Error", "Invalid input")
                return

            # Validate expiry date is not in the past
            if expiry_date:
                try:
                    exp_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
                    today = datetime.now().date()
                    if exp_date < today:
                        messagebox.showerror(
                            "Invalid Expiry Date",
                            f"❌ Cannot select a past expiry date!\n\n"
                            f"Selected: {exp_date.strftime('%d-%m-%Y')}\n"
                            f"Today:      {today.strftime('%d-%m-%Y')}\n\n"
                            f"Please choose today or a future date.")
                        return
                except ValueError:
                    pass

            if self.product:
                # Edit
                self.product.name = name
                self.product.category = category
                self.product.cost_price = cost
                self.product.selling_price = selling
                self.product.stock_quantity = stock
                self.product.barcode = barcode
                self.product.expiry_date = expiry_date
                self.storage.update_product(self.product)
                # Regenerate barcode and QR code images
                if barcode:
                    self.barcode_mgr.generate_barcode(barcode, self.product.product_id)
                    self.barcode_mgr.generate_qr_code(barcode, self.product.product_id)
                messagebox.showinfo("Success", "Product updated")
            else:
                # Add new
                product = Product(
                    name=name,
                    category=category,
                    cost_price=cost,
                    selling_price=selling,
                    stock_quantity=stock,
                    barcode=barcode,
                    expiry_date=expiry_date
                )
                self.storage.add_product(product)
                # Generate barcode image and QR code image
                if barcode:
                    self.barcode_mgr.generate_barcode(barcode, product.product_id)
                    self.barcode_mgr.generate_qr_code(barcode, product.product_id)
                messagebox.showinfo("Success", "Product added")

            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid number format")
