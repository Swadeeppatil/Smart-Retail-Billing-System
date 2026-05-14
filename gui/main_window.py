"""Main application window"""

import tkinter as tk
from tkinter import ttk, messagebox
from gui.login_window import LoginWindow
from gui.dashboard import DashboardWindow
from gui.products import ProductWindow
from gui.billing import BillingWindow
from gui.reports import ReportsWindow
from gui.settings import SettingsWindow
from utils.storage import StorageManager
from utils.auth import AuthManager
from utils.billing import BillingEngine
from utils.barcode import BarcodeManager
from utils.voice_command import VoiceCommandManager, VoiceCommandWidget
from utils.audit_log import AuditLogger
from utils.theme_manager import ThemeManager
from utils.notifications import NotificationManager
from utils.discount_engine import DiscountEngine
from utils.expense_tracker import ExpenseTracker
from utils.demand_forecast import DemandForecaster
from utils.gst_report import GSTReportGenerator
from utils.excel_export import ExcelExporter
from utils.email_service import EmailService
from utils.nlp_query import NLPQueryEngine
from utils.sales_goals import SalesGoalTracker
from utils.loyalty import LoyaltyManager
from utils.supplier import SupplierManager
from utils.bulk_import import BulkImporter
from utils.waste_tracker import WasteTracker
from utils.returns import ReturnManager
from utils.label_printer import LabelPrinter
from models.models import User
from datetime import datetime, timedelta
import tkinter.simpledialog as simpledialog


class MainWindow:
    """Main application window"""

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Retail Billing System")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 600)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Theme manager
        self.theme_mgr = ThemeManager()
        self.theme_mgr.register_callback(self._on_theme_change)
        
        # Apply initial theme
        style = ttk.Style()
        self.theme_mgr.apply_to_style(style)
        self.theme_mgr.apply_to_root(self.root)

        # Initialize managers
        self.storage = StorageManager()
        self.auth = AuthManager(self.storage)
        self.billing = BillingEngine(self.storage)
        self.barcode_mgr = BarcodeManager()
        self.audit = AuditLogger()
        self.notifier = NotificationManager()
        self.discount_engine = DiscountEngine()
        self.expense_tracker = ExpenseTracker()
        self.forecaster = DemandForecaster(self.storage)
        self.gst_report = GSTReportGenerator(self.storage)
        self.excel_exporter = ExcelExporter(self.storage, self.billing)
        self.email_service = EmailService()
        self.nlp = NLPQueryEngine(self.storage)
        self.sales_goals = SalesGoalTracker(self.storage)
        self.loyalty = LoyaltyManager()
        self.supplier_mgr = SupplierManager()
        self.bulk_importer = BulkImporter(self.storage, self.barcode_mgr)
        self.waste_tracker = WasteTracker()
        self.return_mgr = ReturnManager()
        self.label_printer = LabelPrinter()
        
        # Voice command manager
        self.voice_mgr = VoiceCommandManager()
        self.voice_mgr.set_command_callback(self._handle_voice_command)
        
        self.current_user = None
        self.login_window = None
        # track currently opened Toplevel (dashboard/products/etc)
        self.active_window = None
        
        # Ensure at least one admin user exists
        self.ensure_admin_exists()
        
        # Show login
        self.show_login()

    def close_active_window(self):
        """Close any previously opened Toplevel window"""
        if self.active_window is not None:
            try:
                self.active_window.destroy()
            except Exception:
                pass
            self.active_window = None

    def ensure_admin_exists(self):
        """Ensure at least one admin user exists"""
        users = self.storage.get_all_users()
        if not users:
            # Create default admin
            self.auth.create_user("admin", "admin123", "admin", "Administrator")

    def show_login(self):
        """Show login window"""
        self.login_window = LoginWindow(self.root, self.storage, self.auth)
        self.login_window.on_login_success = self.on_login_success

    def on_login_success(self, user: User):
        """Handle successful login"""
        self.current_user = user
        self.audit.log(user.username, "Logged in", "LOGIN",
                       f"User '{user.name}' logged in as {user.role}")
        self.setup_main_ui()
        # Show auto-alerts after login
        self.root.after(500, self._show_login_alerts)

    def setup_main_ui(self):
        """Setup main UI after login"""
        # Clear root
        for widget in self.root.winfo_children():
            widget.destroy()

        c = self.theme_mgr.colors

        # Header frame
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(header_frame, text="Smart Retail Billing System", font=("Arial", 16, "bold")).pack(anchor=tk.W)
        user_frame = ttk.Frame(header_frame)
        user_frame.pack(anchor=tk.E)
        ttk.Label(user_frame, text=f"User: {self.current_user.name} ({self.current_user.role})", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)

        # Dark mode toggle button
        theme_text = "🌙 Dark" if not self.theme_mgr.is_dark else "☀️ Light"
        self.theme_btn = ttk.Button(user_frame, text=theme_text, command=self._toggle_theme, width=10)
        self.theme_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(user_frame, text="Logout", command=self.logout).pack(side=tk.LEFT, padx=5)

        # Voice command bar
        voice_frame = ttk.Frame(self.root)
        voice_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        self.voice_widget = VoiceCommandWidget(voice_frame, self.voice_mgr)
        self.voice_widget.pack(side=tk.LEFT)

        # Keyboard shortcuts hint
        shortcut_label = ttk.Label(voice_frame,
                                    text="  ⌨ F1:Dashboard  F2:Products  F3:Billing  F4:Reports  F5:Settings  F9:DarkMode  F10:Audit",
                                    font=("Arial", 8), foreground=c.get('warning', '#f39c12'))
        shortcut_label.pack(side=tk.RIGHT, padx=10)

        # Separator
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X)

        # Menu buttons frame - Row 1
        menu_frame = ttk.Frame(self.root, padding="5")
        menu_frame.pack(fill=tk.X)
        for i in range(5):
            menu_frame.columnconfigure(i, weight=1)
        ttk.Button(menu_frame, text="📊 Dashboard", command=self.open_dashboard).grid(row=0, column=0, padx=3, pady=3, sticky=tk.EW)
        ttk.Button(menu_frame, text="📦 Products", command=self.open_products).grid(row=0, column=1, padx=3, pady=3, sticky=tk.EW)
        ttk.Button(menu_frame, text="💳 Billing", command=self.open_billing).grid(row=0, column=2, padx=3, pady=3, sticky=tk.EW)
        ttk.Button(menu_frame, text="📈 Reports", command=self.open_reports).grid(row=0, column=3, padx=3, pady=3, sticky=tk.EW)
        ttk.Button(menu_frame, text="⚙️ Settings", command=self.open_settings).grid(row=0, column=4, padx=3, pady=3, sticky=tk.EW)

        # Menu buttons frame - Row 2 (Advanced)
        menu_frame2 = ttk.Frame(self.root, padding="5")
        menu_frame2.pack(fill=tk.X)
        for i in range(5):
            menu_frame2.columnconfigure(i, weight=1)
        ttk.Button(menu_frame2, text="📋 Audit Log", command=self.open_audit_log).grid(row=0, column=0, padx=3, pady=3, sticky=tk.EW)
        ttk.Button(menu_frame2, text="💰 Expenses", command=self.open_expenses).grid(row=0, column=1, padx=3, pady=3, sticky=tk.EW)
        ttk.Button(menu_frame2, text="🤖 Forecasting", command=self.open_forecasting).grid(row=0, column=2, padx=3, pady=3, sticky=tk.EW)
        ttk.Button(menu_frame2, text="🧾 GST Report", command=self.open_gst_report).grid(row=0, column=3, padx=3, pady=3, sticky=tk.EW)
        ttk.Button(menu_frame2, text="📤 Excel Export", command=self.export_excel).grid(row=0, column=4, padx=3, pady=3, sticky=tk.EW)

        # Menu buttons frame - Row 3 (New Features)
        menu_frame3 = ttk.Frame(self.root, padding="5")
        menu_frame3.pack(fill=tk.X)
        for i in range(5):
            menu_frame3.columnconfigure(i, weight=1)
        ttk.Button(menu_frame3, text="🏆 Sales Goals", command=self.open_sales_goals).grid(row=0, column=0, padx=3, pady=3, sticky=tk.EW)
        ttk.Button(menu_frame3, text="⭐ Loyalty", command=self.open_loyalty).grid(row=0, column=1, padx=3, pady=3, sticky=tk.EW)
        ttk.Button(menu_frame3, text="🚚 Suppliers", command=self.open_suppliers).grid(row=0, column=2, padx=3, pady=3, sticky=tk.EW)
        ttk.Button(menu_frame3, text="🗑️ Waste Log", command=self.open_waste).grid(row=0, column=3, padx=3, pady=3, sticky=tk.EW)
        ttk.Button(menu_frame3, text="🔄 Returns", command=self.open_returns).grid(row=0, column=4, padx=3, pady=3, sticky=tk.EW)

        # NLP Query Bar
        query_frame = ttk.LabelFrame(self.root, text="💬 Ask Me Anything", padding="5")
        query_frame.pack(fill=tk.X, padx=10, pady=5)
        self.nlp_entry = ttk.Entry(query_frame, width=60, font=("Arial", 11))
        self.nlp_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.nlp_entry.insert(0, "Try: 'top 5 products' or 'revenue today' or 'low stock'")
        self.nlp_entry.bind('<FocusIn>', lambda e: self.nlp_entry.delete(0, tk.END) if 'Try:' in self.nlp_entry.get() else None)
        self.nlp_entry.bind('<Return>', lambda e: self._run_nlp_query())
        ttk.Button(query_frame, text="🔍 Ask", command=self._run_nlp_query).pack(side=tk.LEFT, padx=5)

        # NLP Answer area
        self.nlp_answer = tk.Text(self.root, height=6, font=("Consolas", 10), wrap=tk.WORD,
                                   bg=c.get('card_bg', 'white'), fg=c.get('card_fg', '#333'))
        self.nlp_answer.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.nlp_answer.insert("1.0", f"Welcome, {self.current_user.name}! Type a question above or use the menu buttons.\n\n"
                                       "💡 Try: 'revenue today', 'top 5 products', 'stock value', 'help'")

        # Bind keyboard shortcuts
        self._bind_shortcuts()


    # ── Keyboard Shortcuts ───────────────────────────────────────────
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts to root"""
        self.root.bind('<F1>', lambda e: self.open_dashboard())
        self.root.bind('<F2>', lambda e: self.open_products())
        self.root.bind('<F3>', lambda e: self.open_billing())
        self.root.bind('<F4>', lambda e: self.open_reports())
        self.root.bind('<F5>', lambda e: self.open_settings())
        self.root.bind('<F9>', lambda e: self._toggle_theme())
        self.root.bind('<F10>', lambda e: self.open_audit_log())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<Control-l>', lambda e: self.logout())

    # ── Dark Mode ────────────────────────────────────────────────────
    def _toggle_theme(self):
        """Toggle dark/light mode"""
        self.theme_mgr.toggle()
        style = ttk.Style()
        self.theme_mgr.apply_to_style(style)
        self.theme_mgr.apply_to_root(self.root)
        self.audit.log(self.current_user.username, f"Switched to {self.theme_mgr.colors['name']}",
                       "SETTINGS", "")
        # Rebuild UI to apply new colors
        self.setup_main_ui()

    def _on_theme_change(self, colors):
        """Callback when theme changes"""
        pass  # handled by setup_main_ui rebuild

    # ── Auto Alerts on Login ─────────────────────────────────────────
    def _show_login_alerts(self):
        """Show low-stock and expiry alerts automatically after login"""
        products = self.storage.get_all_products()
        today = datetime.now().date()
        limit_30 = today + timedelta(days=30)

        # Low stock items
        low_stock = [p for p in products if p.stock_quantity <= 10]

        # Expired / expiring items
        expired = []
        expiring_soon = []
        for p in products:
            if hasattr(p, 'expiry_date') and p.expiry_date:
                for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d'):
                    try:
                        exp_date = datetime.strptime(p.expiry_date.strip(), fmt).date()
                        if exp_date < today:
                            expired.append(p)
                        elif exp_date <= limit_30:
                            expiring_soon.append(p)
                        break
                    except ValueError:
                        continue

        # Build alert message
        alerts = []
        if low_stock:
            names = ", ".join(p.name for p in low_stock[:5])
            more = f" +{len(low_stock)-5} more" if len(low_stock) > 5 else ""
            alerts.append(f"📦 LOW STOCK ({len(low_stock)} items):\n   {names}{more}")

        if expired:
            names = ", ".join(p.name for p in expired[:5])
            more = f" +{len(expired)-5} more" if len(expired) > 5 else ""
            alerts.append(f"❌ EXPIRED ({len(expired)} items):\n   {names}{more}")

        if expiring_soon:
            names = ", ".join(p.name for p in expiring_soon[:5])
            more = f" +{len(expiring_soon)-5} more" if len(expiring_soon) > 5 else ""
            alerts.append(f"⚠️ EXPIRING SOON ({len(expiring_soon)} items):\n   {names}{more}")

        if alerts:
            alert_msg = "\n\n".join(alerts)
            messagebox.showwarning(
                "⚠️ System Alerts",
                f"Hello {self.current_user.name}, please review:\n\n{alert_msg}\n\n"
                f"Open Dashboard for details.",
                parent=self.root
            )
            self.audit.log(self.current_user.username, "Login alerts shown", "SYSTEM",
                           f"Low stock: {len(low_stock)}, Expired: {len(expired)}, "
                           f"Expiring soon: {len(expiring_soon)}")

    # ── Navigation ───────────────────────────────────────────────────
    def open_dashboard(self):
        """Open dashboard window"""
        self.close_active_window()
        win = DashboardWindow(self.root, self.storage, self.current_user)
        self.active_window = getattr(win, 'window', None)
        self.audit.log(self.current_user.username, "Opened Dashboard", "SYSTEM", "")

    def open_products(self):
        """Open products window"""
        self.close_active_window()
        win = ProductWindow(self.root, self.storage, self.barcode_mgr)
        self.active_window = getattr(win, 'window', None)
        self.audit.log(self.current_user.username, "Opened Products", "PRODUCT", "")

    def open_billing(self):
        """Open billing window"""
        self.close_active_window()
        win = BillingWindow(self.root, self.storage, self.billing, self.barcode_mgr, self.current_user)
        self.active_window = getattr(win, 'window', None)
        self.audit.log(self.current_user.username, "Opened Billing", "BILLING", "")

    def open_reports(self):
        """Open reports window"""
        self.close_active_window()
        win = ReportsWindow(self.root, self.storage, self.billing)
        self.active_window = getattr(win, 'window', None)
        self.audit.log(self.current_user.username, "Opened Reports", "SYSTEM", "")

    def open_settings(self):
        """Open settings window"""
        self.close_active_window()
        win = SettingsWindow(self.root, self.storage, self.auth, self.current_user)
        self.active_window = getattr(win, 'window', None)
        self.audit.log(self.current_user.username, "Opened Settings", "SETTINGS", "")

    def open_audit_log(self):
        """Open audit log viewer"""
        self.close_active_window()
        win = AuditLogWindow(self.root, self.audit, self.theme_mgr)
        self.active_window = getattr(win, 'window', None)

    def open_expenses(self):
        """Open expense tracker window"""
        self.close_active_window()
        win = ExpenseWindow(self.root, self.expense_tracker, self.storage, self.theme_mgr)
        self.active_window = getattr(win, 'window', None)
        self.audit.log(self.current_user.username, "Opened Expenses", "SYSTEM", "")

    def open_forecasting(self):
        """Open AI forecasting window"""
        self.close_active_window()
        win = ForecastWindow(self.root, self.forecaster, self.theme_mgr)
        self.active_window = getattr(win, 'window', None)
        self.audit.log(self.current_user.username, "Opened Forecasting", "SYSTEM", "")

    def open_gst_report(self):
        """Open GST report window"""
        self.close_active_window()
        win = GSTReportWindow(self.root, self.gst_report, self.theme_mgr)
        self.active_window = getattr(win, 'window', None)
        self.audit.log(self.current_user.username, "Opened GST Report", "SYSTEM", "")

    def export_excel(self):
        """Export full report to Excel"""
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"report_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )
        if filepath:
            try:
                self.excel_exporter.export_full_report(filepath)
                self.audit.log(self.current_user.username, "Exported Excel report", "SYSTEM", filepath)
                self.notifier.notify("📤 Export Complete", f"Excel report saved!")
                messagebox.showinfo("Success", f"Excel report exported:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")

    def _run_nlp_query(self):
        """Run NLP query"""
        q = self.nlp_entry.get().strip()
        if not q or 'Try:' in q:
            return
        answer = self.nlp.query(q)
        self.nlp_answer.delete("1.0", tk.END)
        self.nlp_answer.insert("1.0", answer)
        self.audit.log(self.current_user.username, f"NLP Query: {q}", "SYSTEM", "")

    def open_sales_goals(self):
        self.close_active_window()
        win = SalesGoalWindow(self.root, self.sales_goals, self.theme_mgr)
        self.active_window = getattr(win, 'window', None)

    def open_loyalty(self):
        self.close_active_window()
        win = LoyaltyWindow(self.root, self.loyalty, self.theme_mgr)
        self.active_window = getattr(win, 'window', None)

    def open_suppliers(self):
        self.close_active_window()
        win = SupplierWindow(self.root, self.supplier_mgr, self.theme_mgr)
        self.active_window = getattr(win, 'window', None)

    def open_waste(self):
        self.close_active_window()
        win = WasteWindow(self.root, self.waste_tracker, self.storage, self.theme_mgr)
        self.active_window = getattr(win, 'window', None)

    def open_returns(self):
        self.close_active_window()
        win = ReturnWindow(self.root, self.return_mgr, self.storage, self.theme_mgr)
        self.active_window = getattr(win, 'window', None)

    def open_bulk_import(self):
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if filepath:
            if filepath.endswith('.csv'):
                ok, errs = self.bulk_importer.import_csv(filepath)
            else:
                ok, errs = self.bulk_importer.import_excel(filepath)
            msg = f"✅ Imported: {ok} products"
            if errs:
                msg += f"\n⚠️ Errors ({len(errs)}):\n" + "\n".join(errs[:5])
            messagebox.showinfo("Bulk Import", msg)

    def print_labels(self):
        products = self.storage.get_all_products()
        if not products:
            messagebox.showinfo("Info", "No products to print labels for.")
            return
        path = self.label_printer.generate_label_sheet(products)
        messagebox.showinfo("Labels Generated", f"Barcode labels PDF saved:\n{path}")
        try:
            import subprocess
            subprocess.Popen(["start", "", path], shell=True)
        except Exception:
            pass

    def logout(self):

        """Logout current user"""
        if messagebox.askyesno("Confirm", "Logout?"):
            self.voice_mgr.stop_listening()
            self.audit.log(self.current_user.username, "Logged out", "LOGIN", "")
            self.current_user = None
            self.show_login()

    def on_closing(self):
        """Handle window closing"""
        if messagebox.askyesno("Exit", "Do you want to exit?"):
            self.voice_mgr.stop_listening()
            if self.current_user:
                self.audit.log(self.current_user.username, "Application closed", "SYSTEM", "")
            self.root.destroy()

    def _handle_voice_command(self, command_key, raw_text):
        """Handle recognized voice commands"""
        cmd_map = {
            "navigate_dashboard": self.open_dashboard,
            "navigate_products": self.open_products,
            "navigate_billing": self.open_billing,
            "navigate_reports": self.open_reports,
            "navigate_settings": self.open_settings,
            "logout": self.logout,
            "exit_app": self.on_closing,
            "close_window": lambda: self.close_active_window(),
            "show_help": lambda: self.voice_widget.show_help() if hasattr(self, 'voice_widget') else None,
        }
        action = cmd_map.get(command_key)
        if action:
            if self.current_user:
                self.audit.log(self.current_user.username, f"Voice command: {raw_text}",
                               "SYSTEM", f"Mapped to: {command_key}")
            # Schedule on main thread
            self.root.after(0, action)


# ── Audit Log Viewer Window ─────────────────────────────────────────────
class AuditLogWindow:
    """Audit log viewer UI"""

    def __init__(self, parent, audit: AuditLogger, theme_mgr: ThemeManager):
        self.audit = audit
        self.theme_mgr = theme_mgr

        self.window = tk.Toplevel(parent)
        self.window.title("📋 Activity / Audit Log")
        self.window.geometry("1000x600")
        self.window.minsize(900, 500)
        self.window.configure(bg=theme_mgr.colors['bg'])
        try:
            self.window.state("zoomed")
        except Exception:
            pass

        self._setup_ui()
        self._load_logs()

    def _setup_ui(self):
        c = self.theme_mgr.colors

        # Header
        header = ttk.Frame(self.window)
        header.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(header, text="📋 Activity / Audit Log", font=("Arial", 16, "bold")).pack(side=tk.LEFT)

        # Filter bar
        filter_frame = ttk.Frame(self.window)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(filter_frame, text="Filter by:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar(value="ALL")
        categories = ["ALL", "LOGIN", "PRODUCT", "BILLING", "SETTINGS", "SYSTEM"]
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                     values=categories, state="readonly", width=12)
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self._load_logs())

        ttk.Label(filter_frame, text="Rows:").pack(side=tk.LEFT, padx=5)
        self.rows_var = tk.StringVar(value="100")
        rows_combo = ttk.Combobox(filter_frame, textvariable=self.rows_var,
                                   values=["50", "100", "200", "500"], state="readonly", width=6)
        rows_combo.pack(side=tk.LEFT, padx=5)
        rows_combo.bind("<<ComboboxSelected>>", lambda e: self._load_logs())

        ttk.Button(filter_frame, text="🔄 Refresh", command=self._load_logs).pack(side=tk.LEFT, padx=10)
        ttk.Button(filter_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)

        # Treeview
        tree_frame = ttk.Frame(self.window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        cols = ("Time", "User", "Action", "Category", "Details")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=20)
        self.tree.heading("Time", text="Timestamp")
        self.tree.heading("User", text="User")
        self.tree.heading("Action", text="Action")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Details", text="Details")

        self.tree.column("Time", width=170, minwidth=150)
        self.tree.column("User", width=100, minwidth=80)
        self.tree.column("Action", width=200, minwidth=150)
        self.tree.column("Category", width=100, minwidth=80)
        self.tree.column("Details", width=300, minwidth=200)

        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Summary bar
        self.summary_label = ttk.Label(self.window, text="", font=("Arial", 9))
        self.summary_label.pack(fill=tk.X, padx=10, pady=5)

    def _load_logs(self):
        """Load and display audit logs"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        category = self.filter_var.get()
        limit = int(self.rows_var.get())

        if category == "ALL":
            logs = self.audit.get_recent_logs(limit)
        else:
            logs = self.audit.get_logs_by_category(category, limit)

        for log in logs:
            ts = log.get('timestamp', '')[:19].replace('T', ' ')
            self.tree.insert("", tk.END, values=(
                ts,
                log.get('user', ''),
                log.get('action', ''),
                log.get('category', ''),
                log.get('details', '')
            ))

        self.summary_label.config(text=f"Showing {len(logs)} entries | Filter: {category}")


# ── Expense Tracker Window ───────────────────────────────────────────────
class ExpenseWindow:
    def __init__(self, parent, expense_tracker, storage, theme_mgr):
        self.et = expense_tracker
        self.storage = storage
        self.window = tk.Toplevel(parent)
        self.window.title("💰 Expense Tracker & P&L")
        self.window.geometry("900x650")
        self.window.configure(bg=theme_mgr.colors['bg'])
        try:
            self.window.state("zoomed")
        except Exception:
            pass
        self._build()

    def _build(self):
        nb = ttk.Notebook(self.window)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Add/View Expenses
        exp_frame = ttk.Frame(nb)
        nb.add(exp_frame, text="📝 Expenses")

        add_f = ttk.LabelFrame(exp_frame, text="Add Expense", padding="10")
        add_f.pack(fill=tk.X, padx=10, pady=10)

        from utils.expense_tracker import EXPENSE_CATEGORIES
        ttk.Label(add_f, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
        self.date_e = ttk.Entry(add_f, width=15)
        self.date_e.grid(row=0, column=1, padx=5)
        self.date_e.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(add_f, text="Category:").grid(row=0, column=2, padx=5)
        self.cat_var = tk.StringVar(value="Miscellaneous")
        ttk.Combobox(add_f, textvariable=self.cat_var, values=EXPENSE_CATEGORIES,
                     state="readonly", width=15).grid(row=0, column=3, padx=5)

        ttk.Label(add_f, text="Amount ₹:").grid(row=1, column=0, padx=5, pady=5)
        self.amt_e = ttk.Entry(add_f, width=15)
        self.amt_e.grid(row=1, column=1, padx=5)

        ttk.Label(add_f, text="Description:").grid(row=1, column=2, padx=5)
        self.desc_e = ttk.Entry(add_f, width=25)
        self.desc_e.grid(row=1, column=3, padx=5)

        ttk.Button(add_f, text="➕ Add Expense", command=self._add).grid(row=1, column=4, padx=10)

        # Treeview
        tree_f = ttk.Frame(exp_frame)
        tree_f.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        cols = ("Date", "Category", "Amount", "Description")
        self.tree = ttk.Treeview(tree_f, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=150)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Scrollbar(tree_f, orient=tk.VERTICAL, command=self.tree.yview).pack(side=tk.RIGHT, fill=tk.Y)
        self._refresh()

        # Tab 2: P&L Statement
        pnl_frame = ttk.Frame(nb)
        nb.add(pnl_frame, text="📊 Profit & Loss")

        pnl_ctrl = ttk.Frame(pnl_frame)
        pnl_ctrl.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(pnl_ctrl, text="From:").pack(side=tk.LEFT, padx=5)
        self.pnl_from = ttk.Entry(pnl_ctrl, width=12)
        self.pnl_from.pack(side=tk.LEFT)
        self.pnl_from.insert(0, datetime.now().replace(day=1).strftime("%Y-%m-%d"))
        ttk.Label(pnl_ctrl, text="To:").pack(side=tk.LEFT, padx=5)
        self.pnl_to = ttk.Entry(pnl_ctrl, width=12)
        self.pnl_to.pack(side=tk.LEFT)
        self.pnl_to.insert(0, datetime.now().strftime("%Y-%m-%d"))
        ttk.Button(pnl_ctrl, text="Generate P&L", command=self._gen_pnl).pack(side=tk.LEFT, padx=10)

        self.pnl_text = tk.Text(pnl_frame, height=20, font=("Courier", 10), wrap=tk.WORD)
        self.pnl_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        ttk.Button(self.window, text="Close", command=self.window.destroy).pack(pady=5)

    def _add(self):
        try:
            self.et.add_expense(self.date_e.get(), self.cat_var.get(),
                                float(self.amt_e.get()), self.desc_e.get())
            self.amt_e.delete(0, tk.END)
            self.desc_e.delete(0, tk.END)
            self._refresh()
            messagebox.showinfo("Success", "Expense added!")
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")

    def _refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for e in self.et.get_expenses():
            self.tree.insert("", tk.END, values=(e["date"], e["category"],
                             f"₹{e['amount']:.2f}", e.get("description", "")))

    def _gen_pnl(self):
        pnl = self.et.generate_pnl(self.pnl_from.get(), self.pnl_to.get(), self.storage)
        self.pnl_text.delete("1.0", tk.END)
        txt = f"""
{'='*50}
    PROFIT & LOSS STATEMENT
    Period: {pnl['period']}
{'='*50}

REVENUE
    Total Revenue:        ₹{pnl['total_revenue']:>12,.2f}
    Less: GST Collected:  ₹{pnl['total_gst']:>12,.2f}
    Less: COGS:           ₹{pnl['cogs']:>12,.2f}
                          {'─'*16}
    GROSS PROFIT:         ₹{pnl['gross_profit']:>12,.2f}

OPERATING EXPENSES
"""
        for cat, amt in pnl['expense_breakdown'].items():
            txt += f"    {cat:<22}₹{amt:>12,.2f}\n"
        txt += f"""                          {'─'*16}
    Total Expenses:       ₹{pnl['total_expenses']:>12,.2f}

{'='*50}
    NET PROFIT:           ₹{pnl['net_profit']:>12,.2f}
    Profit Margin:        {pnl['profit_margin']:.1f}%
    Total Invoices:       {pnl['invoice_count']}
{'='*50}
"""
        self.pnl_text.insert("1.0", txt)


# ── Forecast Window ──────────────────────────────────────────────────────
class ForecastWindow:
    def __init__(self, parent, forecaster, theme_mgr):
        self.fc = forecaster
        self.window = tk.Toplevel(parent)
        self.window.title("🤖 AI Demand Forecasting & ABC Analysis")
        self.window.geometry("1000x600")
        self.window.configure(bg=theme_mgr.colors['bg'])
        try:
            self.window.state("zoomed")
        except Exception:
            pass
        self._build()

    def _build(self):
        nb = ttk.Notebook(self.window)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Demand Forecast
        fc_frame = ttk.Frame(nb)
        nb.add(fc_frame, text="📈 Demand Forecast")
        ttk.Label(fc_frame, text="AI-Predicted Demand (Next 7 Days)", font=("Arial", 14, "bold")).pack(pady=10)

        cols = ("Product", "Stock", "Avg Daily", "Predicted", "Days Left", "Trend", "Reorder Qty")
        self.fc_tree = ttk.Treeview(fc_frame, columns=cols, show="headings", height=15)
        for c in cols:
            self.fc_tree.heading(c, text=c)
            self.fc_tree.column(c, width=120)
        self.fc_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        forecasts = self.fc.forecast_demand(7, 20)
        for f in forecasts:
            tag = "danger" if f["reorder"] else ""
            self.fc_tree.insert("", tk.END, values=(
                f["product_name"], f["current_stock"], f["avg_daily"],
                f["predicted"], f["days_stockout"], f["trend"], f["reorder_qty"]
            ), tags=(tag,))
        self.fc_tree.tag_configure("danger", foreground="red")

        if not forecasts:
            ttk.Label(fc_frame, text="No sales data yet. Start selling to see forecasts!").pack()

        # Tab 2: ABC Analysis
        abc_frame = ttk.Frame(nb)
        nb.add(abc_frame, text="📊 ABC Analysis")
        ttk.Label(abc_frame, text="ABC Inventory Classification (Pareto 80/20)", font=("Arial", 14, "bold")).pack(pady=10)

        abc_data = self.fc.get_abc_analysis()
        abc_tree = ttk.Treeview(abc_frame, columns=("Class", "Product", "Category", "Revenue", "% Total", "Stock"),
                                show="headings", height=15)
        for c in ("Class", "Product", "Category", "Revenue", "% Total", "Stock"):
            abc_tree.heading(c, text=c)
            abc_tree.column(c, width=120)

        colors = {"A": "#27ae60", "B": "#f39c12", "C": "#e74c3c"}
        for cls in ["A", "B", "C"]:
            for item in abc_data.get(cls, []):
                abc_tree.insert("", tk.END, values=(
                    f"Class {cls}", item["name"], item["category"],
                    f"₹{item['revenue']:.2f}", f"{item['pct']}%", item["stock"]
                ), tags=(cls,))
            abc_tree.tag_configure(cls, foreground=colors[cls])

        abc_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        if not any(abc_data.values()):
            ttk.Label(abc_frame, text="No sales data for ABC analysis.").pack()

        # Summary
        summary = ttk.Frame(abc_frame)
        summary.pack(fill=tk.X, padx=10, pady=5)
        for cls, label in [("A", "A (Top 80% Revenue)"), ("B", "B (Next 15%)"), ("C", "C (Bottom 5%)")]:
            count = len(abc_data.get(cls, []))
            ttk.Label(summary, text=f"  {label}: {count} products  ",
                      font=("Arial", 10, "bold"), foreground=colors[cls]).pack(side=tk.LEFT, padx=10)

        ttk.Button(self.window, text="Close", command=self.window.destroy).pack(pady=5)


# ── GST Report Window ────────────────────────────────────────────────────
class GSTReportWindow:
    def __init__(self, parent, gst_gen, theme_mgr):
        self.gst = gst_gen
        self.window = tk.Toplevel(parent)
        self.window.title("🧾 GST Return Report (GSTR-1)")
        self.window.geometry("1000x600")
        self.window.configure(bg=theme_mgr.colors['bg'])
        try:
            self.window.state("zoomed")
        except Exception:
            pass
        self._build()

    def _build(self):
        ctrl = ttk.Frame(self.window)
        ctrl.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(ctrl, text="From:").pack(side=tk.LEFT, padx=5)
        self.from_e = ttk.Entry(ctrl, width=12)
        self.from_e.pack(side=tk.LEFT)
        self.from_e.insert(0, datetime.now().replace(day=1).strftime("%Y-%m-%d"))
        ttk.Label(ctrl, text="To:").pack(side=tk.LEFT, padx=5)
        self.to_e = ttk.Entry(ctrl, width=12)
        self.to_e.pack(side=tk.LEFT)
        self.to_e.insert(0, datetime.now().strftime("%Y-%m-%d"))
        ttk.Button(ctrl, text="Generate", command=self._generate).pack(side=tk.LEFT, padx=10)
        ttk.Button(ctrl, text="📤 Export CSV", command=self._export).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl, text="Close", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)

        # Results
        self.text = tk.Text(self.window, font=("Courier", 10), wrap=tk.WORD)
        self.text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._generate()

    def _generate(self):
        data = self.gst.generate_gstr1_data(self.from_e.get(), self.to_e.get())
        self.text.delete("1.0", tk.END)
        o = data["overall"]
        txt = f"""
{'='*60}
    GSTR-1 SUMMARY REPORT
    Period: {self.from_e.get()} to {self.to_e.get()}
{'='*60}

OVERALL SUMMARY
    Total Invoices:       {o['total_invoices']}
    Total Taxable Value:  ₹{o['total_taxable']:>12,.2f}
    Total CGST:           ₹{o['total_cgst']:>12,.2f}
    Total SGST:           ₹{o['total_sgst']:>12,.2f}
    Total Tax:            ₹{o['total_tax']:>12,.2f}
    Total Revenue:        ₹{o['total_revenue']:>12,.2f}

TAX SLAB WISE BREAKUP
{'─'*60}
{'GST Slab':<12}{'Taxable':>14}{'CGST':>12}{'SGST':>12}{'Count':>10}
{'─'*60}
"""
        for slab, vals in data["tax_summary"].items():
            txt += f"{slab+'%':<12}₹{vals['taxable']:>12,.2f}₹{vals['cgst']:>10,.2f}₹{vals['sgst']:>10,.2f}{vals['count']:>10}\n"

        txt += f"\n{'='*60}\n\nB2C INVOICE DETAILS\n{'─'*60}\n"
        for s in data["b2c_sales"][:50]:
            txt += f"{s['invoice_id']:<20}{s['date']:<12}₹{s['total']:>10,.2f}  GST:{s['gst_rate']}%\n"

        self.text.insert("1.0", txt)
        self._data = data

    def _export(self):
        from tkinter import filedialog
        fp = filedialog.asksaveasfilename(defaultextension=".csv",
                                           filetypes=[("CSV files", "*.csv")])
        if fp:
            if self.gst.export_gstr1_csv(fp, self.from_e.get(), self.to_e.get()):
                messagebox.showinfo("Success", f"GST report exported to:\n{fp}")
            else:
                messagebox.showerror("Error", "Export failed")

# ── Sales Goal Window ────────────────────────────────────────────────────
class SalesGoalWindow:
    def __init__(self, parent, tracker, theme_mgr):
        self.t = tracker
        self.window = tk.Toplevel(parent)
        self.window.title("🏆 Sales Goal Tracker")
        self.window.geometry("800x600")
        self.window.configure(bg=theme_mgr.colors['bg'])
        try: self.window.state("zoomed")
        except: pass
        self._build()

    def _build(self):
        top = ttk.Frame(self.window)
        top.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(top, text="🏆 Sales Goal Tracker", font=("Arial", 16, "bold")).pack(side=tk.LEFT)

        # Set goals
        set_f = ttk.LabelFrame(self.window, text="Set Target", padding="10")
        set_f.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(set_f, text="Type:").grid(row=0, column=0, padx=5)
        self.type_var = tk.StringVar(value="daily")
        ttk.Combobox(set_f, textvariable=self.type_var, values=["daily", "weekly", "monthly"],
                     state="readonly", width=10).grid(row=0, column=1, padx=5)
        ttk.Label(set_f, text="Target ₹:").grid(row=0, column=2, padx=5)
        self.target_e = ttk.Entry(set_f, width=12)
        self.target_e.grid(row=0, column=3, padx=5)
        ttk.Button(set_f, text="Set Goal", command=self._set).grid(row=0, column=4, padx=10)

        # Progress display
        self.canvas = tk.Canvas(self.window, width=700, height=350, bg="white", highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)
        self._draw_progress()

        ttk.Button(self.window, text="🔄 Refresh", command=self._draw_progress).pack(pady=5)
        ttk.Button(self.window, text="Close", command=self.window.destroy).pack(pady=5)

    def _set(self):
        try:
            self.t.set_goal(self.type_var.get(), float(self.target_e.get()))
            messagebox.showinfo("Success", "Goal set!")
            self._draw_progress()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")

    def _draw_progress(self):
        self.canvas.delete("all")
        import math
        types = ["daily", "weekly", "monthly"]
        cx_positions = [120, 350, 580]
        for i, gt in enumerate(types):
            prog = self.t.get_progress(gt)
            cx, cy, r = cx_positions[i], 180, 80
            pct = prog["percentage"] if prog else 0
            target = prog["target"] if prog else 0
            achieved = prog["achieved"] if prog else 0
            # Background ring
            self.canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=90, extent=-360,
                                    outline="#e0e0e0", width=12, style=tk.ARC)
            # Progress ring
            color = "#27ae60" if pct >= 100 else ("#f39c12" if pct >= 50 else "#e74c3c")
            extent = -360 * min(pct, 100) / 100
            self.canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=90, extent=extent,
                                    outline=color, width=12, style=tk.ARC)
            # Text
            self.canvas.create_text(cx, cy-10, text=f"{pct:.0f}%", font=("Arial", 24, "bold"), fill=color)
            self.canvas.create_text(cx, cy+20, text=f"₹{achieved:,.0f}/₹{target:,.0f}", font=("Arial", 9))
            self.canvas.create_text(cx, cy+r+20, text=gt.upper(), font=("Arial", 12, "bold"))

        # Streak
        streak = self.t.get_streak()
        self.canvas.create_text(350, 330, text=f"🔥 Streak: {streak} days", font=("Arial", 12, "bold"),
                                fill="#e74c3c" if streak > 0 else "#999")


# ── Loyalty Window ───────────────────────────────────────────────────────
class LoyaltyWindow:
    def __init__(self, parent, loyalty, theme_mgr):
        self.lm = loyalty
        self.window = tk.Toplevel(parent)
        self.window.title("⭐ Customer Loyalty Program")
        self.window.geometry("900x600")
        self.window.configure(bg=theme_mgr.colors['bg'])
        try: self.window.state("zoomed")
        except: pass
        self._build()

    def _build(self):
        nb = ttk.Notebook(self.window)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Register tab
        reg = ttk.Frame(nb); nb.add(reg, text="➕ Register")
        rf = ttk.LabelFrame(reg, text="New Customer", padding="10")
        rf.pack(padx=10, pady=10, fill=tk.X)
        ttk.Label(rf, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_e = ttk.Entry(rf, width=20); self.name_e.grid(row=0, column=1, padx=5)
        ttk.Label(rf, text="Phone:").grid(row=0, column=2, padx=5)
        self.phone_e = ttk.Entry(rf, width=15); self.phone_e.grid(row=0, column=3, padx=5)
        ttk.Label(rf, text="Email:").grid(row=0, column=4, padx=5)
        self.email_e = ttk.Entry(rf, width=20); self.email_e.grid(row=0, column=5, padx=5)
        ttk.Button(rf, text="Register", command=self._register).grid(row=0, column=6, padx=10)

        # Members tab
        mem = ttk.Frame(nb); nb.add(mem, text="👥 Members")
        cols = ("Name", "Phone", "Points", "Tier", "Total Spent", "Visits")
        self.tree = ttk.Treeview(mem, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c); self.tree.column(c, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._refresh()

        # Lookup tab
        lu = ttk.Frame(nb); nb.add(lu, text="🔍 Lookup")
        luf = ttk.Frame(lu); luf.pack(padx=10, pady=10, fill=tk.X)
        ttk.Label(luf, text="Phone:").pack(side=tk.LEFT, padx=5)
        self.lu_phone = ttk.Entry(luf, width=15); self.lu_phone.pack(side=tk.LEFT, padx=5)
        ttk.Button(luf, text="Lookup", command=self._lookup).pack(side=tk.LEFT, padx=5)
        self.lu_result = tk.Text(lu, height=15, font=("Consolas", 10))
        self.lu_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        ttk.Button(self.window, text="Close", command=self.window.destroy).pack(pady=5)

    def _register(self):
        name, phone = self.name_e.get().strip(), self.phone_e.get().strip()
        if not name or not phone:
            messagebox.showerror("Error", "Name and phone required"); return
        self.lm.register_customer(name, phone, self.email_e.get().strip())
        messagebox.showinfo("Success", f"Customer {name} registered!")
        self._refresh()

    def _refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for c in self.lm.get_all_customers():
            tier = self.lm.get_tier(c['phone'])
            self.tree.insert("", tk.END, values=(c['name'], c['phone'], c['points'],
                             tier, f"₹{c['total_spent']:.0f}", c['visit_count']))

    def _lookup(self):
        cust = self.lm.find_customer(self.lu_phone.get().strip())
        self.lu_result.delete("1.0", tk.END)
        if not cust:
            self.lu_result.insert("1.0", "Customer not found.")
            return
        tier = self.lm.get_tier(cust['phone'])
        from utils.loyalty import LOYALTY_TIERS
        self.lu_result.insert("1.0", f"""
⭐ LOYALTY CARD
{'='*40}
Name:       {cust['name']}
Phone:      {cust['phone']}
Tier:       {tier} {'🥉' if tier=='Bronze' else '🥈' if tier=='Silver' else '🥇' if tier=='Gold' else '💎'}
Points:     {cust['points']}
Total Spent: ₹{cust['total_spent']:,.2f}
Visits:     {cust['visit_count']}
Last Visit: {cust.get('last_visit', 'N/A')[:10]}
{'='*40}
""")


# ── Supplier Window ──────────────────────────────────────────────────────
class SupplierWindow:
    def __init__(self, parent, supplier_mgr, theme_mgr):
        self.sm = supplier_mgr
        self.window = tk.Toplevel(parent)
        self.window.title("🚚 Supplier Management")
        self.window.geometry("900x600")
        self.window.configure(bg=theme_mgr.colors['bg'])
        try: self.window.state("zoomed")
        except: pass
        self._build()

    def _build(self):
        nb = ttk.Notebook(self.window)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add Supplier
        af = ttk.Frame(nb); nb.add(af, text="➕ Add Supplier")
        sf = ttk.LabelFrame(af, text="New Supplier", padding="10")
        sf.pack(padx=10, pady=10, fill=tk.X)
        fields = [("Name:", "s_name", 20), ("Phone:", "s_phone", 15), ("Email:", "s_email", 20),
                  ("Address:", "s_addr", 30), ("Products:", "s_prods", 30)]
        self._entries = {}
        for i, (lbl, key, w) in enumerate(fields):
            ttk.Label(sf, text=lbl).grid(row=i//3, column=(i%3)*2, padx=5, pady=5)
            e = ttk.Entry(sf, width=w); e.grid(row=i//3, column=(i%3)*2+1, padx=5)
            self._entries[key] = e
        ttk.Button(sf, text="Add Supplier", command=self._add).grid(row=2, column=5, padx=10)

        # List
        lf = ttk.Frame(nb); nb.add(lf, text="📋 Suppliers")
        cols = ("ID", "Name", "Phone", "Email", "Products")
        self.tree = ttk.Treeview(lf, columns=cols, show="headings", height=15)
        for c in cols: self.tree.heading(c, text=c); self.tree.column(c, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._refresh()

        # PO
        po = ttk.Frame(nb); nb.add(po, text="📦 Purchase Orders")
        po_cols = ("ID", "Supplier", "Status", "Total", "Date")
        self.po_tree = ttk.Treeview(po, columns=po_cols, show="headings", height=15)
        for c in po_cols: self.po_tree.heading(c, text=c)
        self.po_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._load_pos()

        ttk.Button(self.window, text="Close", command=self.window.destroy).pack(pady=5)

    def _add(self):
        name = self._entries["s_name"].get().strip()
        if not name: messagebox.showerror("Error", "Name required"); return
        self.sm.add_supplier(name, self._entries["s_phone"].get(), self._entries["s_email"].get(),
                             self._entries["s_addr"].get(), self._entries["s_prods"].get())
        messagebox.showinfo("Success", f"Supplier {name} added!")
        self._refresh()

    def _refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for s in self.sm.get_all_suppliers():
            self.tree.insert("", tk.END, values=(s['id'], s['name'], s['phone'], s['email'], s.get('products_supplied', '')))

    def _load_pos(self):
        for i in self.po_tree.get_children(): self.po_tree.delete(i)
        for po in self.sm.get_purchase_orders():
            self.po_tree.insert("", tk.END, values=(po['id'], po['supplier_name'], po['status'],
                                f"₹{po['total_amount']:.0f}", po.get('order_date', '')[:10]))


# ── Waste Window ─────────────────────────────────────────────────────────
class WasteWindow:
    def __init__(self, parent, waste_tracker, storage, theme_mgr):
        self.wt = waste_tracker
        self.storage = storage
        self.window = tk.Toplevel(parent)
        self.window.title("🗑️ Waste & Spoilage Tracker")
        self.window.geometry("900x600")
        self.window.configure(bg=theme_mgr.colors['bg'])
        try: self.window.state("zoomed")
        except: pass
        self._build()

    def _build(self):
        af = ttk.LabelFrame(self.window, text="Log Waste", padding="10")
        af.pack(fill=tk.X, padx=10, pady=10)
        products = self.storage.get_all_products()
        p_names = [p.name for p in products]
        ttk.Label(af, text="Product:").grid(row=0, column=0, padx=5)
        self.prod_var = tk.StringVar()
        ttk.Combobox(af, textvariable=self.prod_var, values=p_names, width=20).grid(row=0, column=1, padx=5)
        ttk.Label(af, text="Qty:").grid(row=0, column=2, padx=5)
        self.qty_e = ttk.Entry(af, width=8); self.qty_e.grid(row=0, column=3, padx=5)
        ttk.Label(af, text="Reason:").grid(row=0, column=4, padx=5)
        from utils.waste_tracker import WASTE_REASONS
        self.reason_var = tk.StringVar(value="Expired")
        ttk.Combobox(af, textvariable=self.reason_var, values=WASTE_REASONS, state="readonly",
                     width=15).grid(row=0, column=5, padx=5)
        ttk.Button(af, text="Log Waste", command=self._log).grid(row=0, column=6, padx=10)

        cols = ("Date", "Product", "Qty", "Reason", "Loss")
        self.tree = ttk.Treeview(self.window, columns=cols, show="headings", height=15)
        for c in cols: self.tree.heading(c, text=c); self.tree.column(c, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Summary
        self.summary_lbl = ttk.Label(self.window, text="", font=("Arial", 10, "bold"))
        self.summary_lbl.pack(padx=10, pady=5)
        self._refresh()
        ttk.Button(self.window, text="Close", command=self.window.destroy).pack(pady=5)

    def _log(self):
        name = self.prod_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Select a product"); return
        try:
            qty = int(self.qty_e.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity"); return
        products = self.storage.get_all_products()
        cost = next((p.cost_price for p in products if p.name == name), 0)
        self.wt.log_waste(datetime.now().strftime("%Y-%m-%d"), name, qty, self.reason_var.get(), cost)
        messagebox.showinfo("Logged", f"Waste logged: {qty}x {name}")
        self._refresh()

    def _refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for w in self.wt.get_all_waste():
            self.tree.insert("", tk.END, values=(w['date'], w['product_name'], w['quantity'],
                             w['reason'], f"₹{w['total_loss']:.2f}"))
        s = self.wt.get_summary()
        self.summary_lbl.config(text=f"Total Waste: {s['total_qty']} items | Total Loss: ₹{s['total_loss']:,.2f}")


# ── Return Window ────────────────────────────────────────────────────────
class ReturnWindow:
    def __init__(self, parent, return_mgr, storage, theme_mgr):
        self.rm = return_mgr
        self.storage = storage
        self.window = tk.Toplevel(parent)
        self.window.title("🔄 Returns & Refunds")
        self.window.geometry("900x600")
        self.window.configure(bg=theme_mgr.colors['bg'])
        try: self.window.state("zoomed")
        except: pass
        self._build()

    def _build(self):
        af = ttk.LabelFrame(self.window, text="Process Return", padding="10")
        af.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(af, text="Invoice ID:").grid(row=0, column=0, padx=5)
        self.inv_e = ttk.Entry(af, width=15); self.inv_e.grid(row=0, column=1, padx=5)
        ttk.Label(af, text="Product:").grid(row=0, column=2, padx=5)
        self.prod_e = ttk.Entry(af, width=20); self.prod_e.grid(row=0, column=3, padx=5)
        ttk.Label(af, text="Qty:").grid(row=0, column=4, padx=5)
        self.qty_e = ttk.Entry(af, width=8); self.qty_e.grid(row=0, column=5, padx=5)
        ttk.Label(af, text="Refund ₹:").grid(row=1, column=0, padx=5, pady=5)
        self.refund_e = ttk.Entry(af, width=12); self.refund_e.grid(row=1, column=1, padx=5)
        ttk.Label(af, text="Reason:").grid(row=1, column=2, padx=5)
        self.reason_e = ttk.Entry(af, width=25); self.reason_e.grid(row=1, column=3, padx=5)
        ttk.Button(af, text="Process Return", command=self._process).grid(row=1, column=5, padx=10)

        cols = ("Invoice", "Product", "Qty", "Refund", "Reason", "Date")
        self.tree = ttk.Treeview(self.window, columns=cols, show="headings", height=15)
        for c in cols: self.tree.heading(c, text=c); self.tree.column(c, width=130)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.summary_lbl = ttk.Label(self.window, text="", font=("Arial", 10, "bold"))
        self.summary_lbl.pack(padx=10, pady=5)
        self._refresh()
        ttk.Button(self.window, text="Close", command=self.window.destroy).pack(pady=5)

    def _process(self):
        inv = self.inv_e.get().strip()
        prod = self.prod_e.get().strip()
        if not inv or not prod:
            messagebox.showerror("Error", "Invoice ID and Product required"); return
        try:
            qty = int(self.qty_e.get())
            refund = float(self.refund_e.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid qty or refund"); return
        self.rm.process_return(inv, prod, qty, refund, self.reason_e.get().strip())
        messagebox.showinfo("Success", f"Return processed: {qty}x {prod}, Refund ₹{refund:.2f}")
        self._refresh()

    def _refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in self.rm.get_all_returns():
            self.tree.insert("", tk.END, values=(r['invoice_id'], r['product_name'], r['quantity'],
                             f"₹{r['refund_amount']:.2f}", r.get('reason', ''), r['created_at'][:10]))
        s = self.rm.get_summary()
        self.summary_lbl.config(text=f"Total Returns: {s['count']} | Items: {s['total_items']} | Refunds: ₹{s['total_refund']:,.2f}")


def main():

    """Main entry point"""
    root = tk.Tk()
    root.geometry("1000x600")
    root.minsize(800, 600)
    
    # Set theme
    style = ttk.Style()
    style.theme_use('clam')
    
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
