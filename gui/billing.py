"""Billing/Invoice creation window"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from utils.storage import StorageManager
from utils.billing import BillingEngine
from utils.barcode import BarcodeManager
from utils.pdf_generator import InvoicePDF
from utils.discount_engine import DiscountEngine
from utils.email_service import EmailService
from models.models import Invoice, Product, BillItem
import subprocess
import os
import tkinter.simpledialog as simpledialog


class BillingWindow:
    """Billing/Invoice creation UI"""

    def __init__(self, parent, storage: StorageManager, billing: BillingEngine, barcode_mgr: BarcodeManager, user, embed_frame=None):
        self.parent = parent
        self.storage = storage
        self.billing = billing
        self.barcode_mgr = barcode_mgr
        self.user = user
        self.pdf_gen = InvoicePDF()
        
        if embed_frame:
            self.window = embed_frame
        else:
            self.window = tk.Toplevel(parent)
            self.window.title("Billing - Create Invoice")
            self.window.geometry("1000x700")
            self.window.minsize(900, 600)
            try:
                self.window.state("zoomed")
            except Exception:
                pass
        
        self.current_invoice = Invoice(created_by=user.name)
        
        self.setup_ui()

    def setup_ui(self):
        """Create billing UI with improved colour scheme"""
        # apply a custom theme/color configuration
        style = ttk.Style()
        style.theme_use('clam')
        # light neutral background for frames/labels
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TLabelframe', background='#f5f5f5', foreground='#333333')
        style.configure('TLabel', background='#f5f5f5', foreground='#333333')
        # accent buttons
        style.configure('TButton', background='#007acc', foreground='white')
        style.map('TButton',
                  background=[('active', '#005f99'), ('disabled', '#cccccc')],
                  foreground=[('disabled', '#888888')])
        # configure combobox/backdrop areas
        style.configure('TCombobox', fieldbackground='white', background='white')
        # set window background
        self.window.configure(bg='#f5f5f5')
        
        # Header with logo and title
        header_frame = ttk.Frame(self.window)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Logo/Title
        title_label = ttk.Label(header_frame, text="💳 Smart Retail Billing System", 
                               font=("Arial", 16, "bold"), foreground="#007acc")
        title_label.pack(side=tk.LEFT, padx=10)
        
        subtitle_label = ttk.Label(header_frame, text="Create Professional Invoices",
                                  font=("Arial", 10), foreground="#666666")
        subtitle_label.pack(side=tk.LEFT, padx=5)
        
        # Separator
        separator = ttk.Separator(self.window, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, padx=10)
        
        # Top frame - Customer and Payment details
        top_frame = ttk.LabelFrame(self.window, text="Customer & Payment Details", padding="10")
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(top_frame, text="Customer Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.customer_name = ttk.Entry(top_frame, width=30)
        self.customer_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(top_frame, text="Phone:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.customer_phone = ttk.Entry(top_frame, width=20)
        self.customer_phone.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(top_frame, text="Payment Mode:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.payment_var = tk.StringVar(value="Cash")
        payment_combo = ttk.Combobox(top_frame, textvariable=self.payment_var, 
                                     values=["Cash", "UPI", "Card"], state="readonly", width=15)
        payment_combo.grid(row=1, column=1, padx=5, pady=5)

        # Product selection frame
        product_frame = ttk.LabelFrame(self.window, text="Add Products", padding="10")
        product_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(product_frame, text="Product:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.product_combo = ttk.Combobox(product_frame, width=40, state="readonly")
        self.product_combo.grid(row=0, column=1, padx=5)
        self.refresh_product_list()

        # scan button
        scan_btn = ttk.Button(product_frame, text="📷 Scan Barcode/QR", command=self.scan_barcode)
        scan_btn.grid(row=0, column=2, padx=5)

        ttk.Label(product_frame, text="Quantity:").grid(row=0, column=3, sticky=tk.W, padx=5)
        self.qty_entry = ttk.Entry(product_frame, width=10)
        self.qty_entry.grid(row=0, column=4, padx=5)
        self.qty_entry.insert(0, "1")

        ttk.Label(product_frame, text="Discount %:").grid(row=0, column=5, sticky=tk.W, padx=5)
        self.discount_entry = ttk.Entry(product_frame, width=10)
        self.discount_entry.grid(row=0, column=6, padx=5)
        self.discount_entry.insert(0, "0")

        ttk.Button(product_frame, text="Add Item", command=self.add_item).grid(row=0, column=7, padx=5)

        # Smart Discount Suggestion
        self.discount_engine = DiscountEngine()
        self.discount_hint = ttk.Label(self.window, text="", font=("Arial", 9, "bold"), foreground="#27ae60")
        self.discount_hint.pack(fill=tk.X, padx=10)

        # Items in invoice
        items_frame = ttk.LabelFrame(self.window, text="Items in Invoice", padding="5")
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview
        self.items_tree = ttk.Treeview(items_frame, columns=("Qty", "Unit Price", "Discount", "Total"), height=5)
        self.items_tree.column("#0", width=300)
        self.items_tree.column("Qty", width=50)
        self.items_tree.column("Unit Price", width=100)
        self.items_tree.column("Discount", width=80)
        self.items_tree.column("Total", width=100)

        self.items_tree.heading("#0", text="Product Name")
        self.items_tree.heading("Qty", text="Qty")
        self.items_tree.heading("Unit Price", text="Unit Price")
        self.items_tree.heading("Discount", text="Discount %")
        self.items_tree.heading("Total", text="Total")

        scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
        self.items_tree.configure(yscroll=scrollbar.set)
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.items_tree.bind("<Button-3>", self.show_item_menu)

        # Totals frame
        totals_frame = ttk.LabelFrame(self.window, text="Totals", padding="10")
        totals_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(totals_frame, text="Subtotal:").grid(row=0, column=0, sticky=tk.W, padx=20)
        self.subtotal_label = ttk.Label(totals_frame, text="₹0.00", font=("Arial", 11, "bold"))
        self.subtotal_label.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(totals_frame, text="Discount %:").grid(row=0, column=2, sticky=tk.W, padx=20)
        self.disc_percent_combo = ttk.Combobox(totals_frame, values=[0, 5, 10, 15, 20], width=10)
        self.disc_percent_combo.grid(row=0, column=3, padx=5)
        self.disc_percent_combo.set(0)
        self.disc_percent_combo.bind("<<ComboboxSelected>>", lambda e: self.update_totals())

        ttk.Label(totals_frame, text="Discount Amount:").grid(row=0, column=4, sticky=tk.W, padx=20)
        self.discount_amount_label = ttk.Label(totals_frame, text="₹0.00", font=("Arial", 11, "bold"))
        self.discount_amount_label.grid(row=0, column=5, sticky=tk.W)

        ttk.Label(totals_frame, text="GST %:").grid(row=1, column=0, sticky=tk.W, padx=20)
        self.gst_combo = ttk.Combobox(totals_frame, values=[0, 5, 12, 18], width=10)
        self.gst_combo.grid(row=1, column=1, padx=5)
        self.gst_combo.set(18)
        self.gst_combo.bind("<<ComboboxSelected>>", lambda e: self.update_totals())

        ttk.Label(totals_frame, text="GST Amount:").grid(row=1, column=2, sticky=tk.W, padx=20)
        self.gst_amount_label = ttk.Label(totals_frame, text="₹0.00", font=("Arial", 11, "bold"))
        self.gst_amount_label.grid(row=1, column=3, sticky=tk.W)

        ttk.Label(totals_frame, text="Grand Total:").grid(row=1, column=4, sticky=tk.W, padx=20)
        self.grand_total_label = ttk.Label(totals_frame, text="₹0.00", font=("Arial", 14, "bold"), foreground="#2ecc71")
        self.grand_total_label.grid(row=1, column=5, sticky=tk.W)

        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        # Configure grid columns
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)
        button_frame.columnconfigure(4, weight=1)
        button_frame.columnconfigure(5, weight=1)

        for i in range(7):
            button_frame.columnconfigure(i, weight=1)
        ttk.Button(button_frame, text="New Invoice", command=self.new_invoice).grid(row=0, column=0, padx=3, pady=3, sticky=tk.W)
        ttk.Button(button_frame, text="🎯 Auto Discount", command=self.apply_smart_discount).grid(row=0, column=1, padx=3, pady=3, sticky=tk.W)
        ttk.Button(button_frame, text="Generate PDF", command=self.generate_pdf).grid(row=0, column=2, padx=3, pady=3, sticky=tk.W)
        ttk.Button(button_frame, text="📧 Email Invoice", command=self.email_invoice).grid(row=0, column=3, padx=3, pady=3, sticky=tk.W)
        ttk.Button(button_frame, text="Send WhatsApp", command=self.send_whatsapp).grid(row=0, column=4, padx=3, pady=3, sticky=tk.W)
        ttk.Button(button_frame, text="UPI QR", command=self.generate_pay_qr).grid(row=0, column=5, padx=3, pady=3, sticky=tk.W)
        ttk.Button(button_frame, text="Finalize & Save", command=self.finalize_invoice).grid(row=0, column=6, padx=3, pady=3, sticky=tk.W)
        ttk.Button(button_frame, text="Close", command=self.window.destroy).grid(row=0, column=7, padx=3, pady=3, sticky=tk.E)

    def refresh_product_list(self):
        """Refresh product dropdown"""
        products = self.storage.get_all_products()
        items = [f"{p.name} (Stock: {p.stock_quantity})" for p in products]
        self.product_combo['values'] = items

    def add_item(self):
        """Add item to invoice"""
        try:
            product_display = self.product_combo.get()
            quantity = int(self.qty_entry.get())
            discount = float(self.discount_entry.get())

            if not product_display or quantity <= 0:
                messagebox.showerror("Error", "Invalid input")
                return

            # Extract product name
            product_name = product_display.split(" (Stock:")[0]
            products = self.storage.get_all_products()
            product = None
            for p in products:
                if p.name == product_name:
                    product = p
                    break

            if not product:
                messagebox.showerror("Error", "Product not found")
                return

            if quantity > product.stock_quantity:
                messagebox.showerror("Error", f"Not enough stock. Available: {product.stock_quantity}")
                return

            # Check if product is expired or expiring soon
            if hasattr(product, 'expiry_date') and product.expiry_date:
                from datetime import datetime, timedelta
                for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d'):
                    try:
                        exp_date = datetime.strptime(product.expiry_date.strip(), fmt).date()
                        today = datetime.now().date()
                        if exp_date < today:
                            messagebox.showerror("Expired Product Error", f"Product '{product.name}' is expired (Expired on {product.expiry_date})! Cannot be billed.")
                            return
                        elif exp_date <= today + timedelta(days=2):
                            messagebox.showwarning("Expiry Warning", f"Warning: Product '{product.name}' will expire in 2 days! (Expires on {product.expiry_date})")
                        break # Found correct format
                    except ValueError:
                        continue

            # Add item
            if self.billing.add_item_to_invoice(self.current_invoice, product, quantity, discount):
                self._play_beep()  # beep sound when product selected
                self.refresh_items_tree()
                self.update_totals()
                self.qty_entry.delete(0, tk.END)
                self.qty_entry.insert(0, "1")
                self.discount_entry.delete(0, tk.END)
                self.discount_entry.insert(0, "0")
            else:
                messagebox.showerror("Error", "Could not add item")
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or discount")

    def refresh_items_tree(self):
        """Refresh items tree"""
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)

        for item in self.current_invoice.items:
            self.items_tree.insert("", tk.END, text=item.product_name, values=(
                item.quantity,
                f"₹{item.unit_price:.2f}",
                f"{item.discount_percent}%",
                f"₹{item.line_total:.2f}"
            ))

    def _play_beep(self):
        """Play a beep sound when product is selected (Windows)"""
        try:
            import winsound
            winsound.Beep(1000, 100)  # frequency 1000Hz, duration 100ms
        except ImportError:
            # fallback for non-Windows or if winsound not available
            try:
                import os
                os.system('beep' if os.name == 'posix' else 'echo \x07')
            except Exception:
                pass  # silently fail if no beep available

    def scan_barcode(self):
        """Open camera/file dialog and scan barcode or QR code, then select product if found"""
        messagebox.showinfo("Scan", "Position the barcode or QR code in front of your camera.\n"
                            "Both barcode and QR code are supported.\n"
                            "Press 'q' to cancel and choose an image file instead.",
                            parent=self.window)
        code = self.barcode_mgr.scan_barcode(parent=self.window)
        if not code:
            return
        product = self.storage.get_product_by_barcode(code)
        if product:
            # Use the same display format as the product combobox
            self.product_combo.set(f"{product.name} (Stock: {product.stock_quantity})")
            messagebox.showinfo("Found", f"Product '{product.name}' selected!", parent=self.window)
        else:
            messagebox.showerror("Not found", f"No product matches scanned code: {code}", parent=self.window)

    def update_totals(self):
        """Update total calculations"""
        try:
            discount_percent = float(self.disc_percent_combo.get() or 0)
            gst_percent = float(self.gst_combo.get() or 18)

            self.current_invoice.discount_percent = discount_percent
            self.current_invoice.gst_percent = gst_percent
            self.current_invoice.calculate_totals()

            self.subtotal_label.config(text=f"₹{self.current_invoice.subtotal:.2f}")
            self.discount_amount_label.config(text=f"₹{self.current_invoice.discount_amount:.2f}")
            self.gst_amount_label.config(text=f"₹{self.current_invoice.gst_amount:.2f}")
            self.grand_total_label.config(text=f"₹{self.current_invoice.grand_total:.2f}")

            # Smart discount hint
            if self.current_invoice.items:
                best = self.discount_engine.get_best_discount(self.current_invoice)
                if best:
                    self.discount_hint.config(
                        text=f"🎯 Smart Discount Available: {best['name']} — Save ₹{best['savings']:.2f}! Click 'Auto Discount' to apply.",
                        foreground="#27ae60")
                else:
                    self.discount_hint.config(text="", foreground="#27ae60")
            else:
                self.discount_hint.config(text="")
        except ValueError:
            pass

    def apply_smart_discount(self):
        """Auto-apply the best available discount"""
        if not self.current_invoice.items:
            messagebox.showinfo("Info", "Add items first to get discount suggestions.")
            return
        best = self.discount_engine.get_best_discount(self.current_invoice)
        if best:
            self.disc_percent_combo.set(best["discount_percent"])
            self.update_totals()
            messagebox.showinfo("🎯 Discount Applied",
                                f"Applied: {best['name']}\n"
                                f"Discount: {best['discount_percent']}%\n"
                                f"You save: ₹{best['savings']:.2f}")
        else:
            all_rules = self.discount_engine.get_all_rules()
            hints = "\n".join(f"• {r.name}" for r in all_rules[:5])
            messagebox.showinfo("No Discount Available",
                                f"No discounts match current invoice.\n\nAvailable rules:\n{hints}")

    def email_invoice(self):
        """Email invoice PDF to customer"""
        if not self.current_invoice.items:
            messagebox.showerror("Error", "Invoice is empty")
            return
        email = simpledialog.askstring("Email Invoice",
                                        "Enter customer email address:",
                                        parent=self.window)
        if not email or "@" not in email:
            return

        # Generate PDF first
        self.current_invoice.customer_name = self.customer_name.get() or "Walk-in Customer"
        self.current_invoice.customer_phone = self.customer_phone.get()
        self.current_invoice.payment_mode = self.payment_var.get()
        self.current_invoice.calculate_totals()

        if not self.pdf_gen.generate_pdf(self.current_invoice):
            messagebox.showerror("Error", "Could not generate PDF for email")
            return

        pdf_path = self.pdf_gen.get_invoice_path(self.current_invoice.invoice_id)
        email_svc = EmailService()
        if not email_svc.is_configured():
            messagebox.showinfo("Email Setup Required",
                                "Email is not configured.\n\n"
                                "To enable, set your Gmail + App Password in:\n"
                                "utils/email_service.py\n\n"
                                "SENDER_EMAIL = 'your@gmail.com'\n"
                                "SENDER_PASSWORD = 'your-app-password'")
            return

        def on_result(success, error):
            if success:
                self.window.after(0, lambda: messagebox.showinfo("Success",
                    f"Invoice emailed to {email}!"))
            else:
                self.window.after(0, lambda: messagebox.showerror("Error",
                    f"Email failed: {error}"))

        email_svc.send_invoice_email(email, self.current_invoice, pdf_path, on_result)
        messagebox.showinfo("Sending...", f"Sending invoice to {email}...")

    def show_item_menu(self, event):
        """Show context menu for items"""
        item = self.items_tree.selection()
        if not item:
            return
        
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="Remove", command=lambda: self.remove_item(item[0]))
        menu.post(event.x_root, event.y_root)

    def remove_item(self, item_id):
        """Remove item from invoice"""
        index = list(self.items_tree.get_children()).index(item_id)
        self.billing.remove_item_from_invoice(self.current_invoice, index)
        self.refresh_items_tree()
        self.update_totals()

    def finalize_invoice(self):
        """Save invoice"""
        if not self.current_invoice.items:
            messagebox.showerror("Error", "Invoice is empty")
            return

        try:
            self.current_invoice.customer_name = self.customer_name.get() or "Walk-in Customer"
            self.current_invoice.customer_phone = self.customer_phone.get()
            self.current_invoice.payment_mode = self.payment_var.get()

            if self.billing.finalize_invoice(self.current_invoice):
                messagebox.showinfo("Success", f"Invoice {self.current_invoice.invoice_id} saved successfully")
                self.new_invoice()
            else:
                messagebox.showerror("Error", "Could not save invoice")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_pdf(self):
        """Generate PDF invoice"""
        if not self.current_invoice.items:
            messagebox.showerror("Error", "Invoice is empty")
            return

        try:
            self.current_invoice.customer_name = self.customer_name.get() or "Walk-in Customer"
            self.current_invoice.customer_phone = self.customer_phone.get()
            self.current_invoice.payment_mode = self.payment_var.get()
            self.current_invoice.calculate_totals()

            if self.pdf_gen.generate_pdf(self.current_invoice):
                pdf_path = self.pdf_gen.get_invoice_path(self.current_invoice.invoice_id)
                if messagebox.askyesno("Success", "PDF generated. Open file?"):
                    try:
                        os.startfile(pdf_path) if os.name == 'nt' else subprocess.run(['open', pdf_path])
                    except:
                        messagebox.showinfo("Info", f"PDF saved at: {pdf_path}")
            else:
                messagebox.showerror("Error", "Could not generate PDF")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def new_invoice(self):
        """Create new invoice"""
        self.current_invoice = Invoice(created_by=self.user.name)
        self.customer_name.delete(0, tk.END)
        self.customer_phone.delete(0, tk.END)
        self.payment_var.set("Cash")
        self.disc_percent_combo.set(0)
        self.gst_combo.set(18)
        self.items_tree.delete(*self.items_tree.get_children())
        self.update_totals()

    def send_whatsapp(self):
        """Format bill details and open WhatsApp"""
        phone = self.customer_phone.get().strip()
        if not phone:
            messagebox.showerror("Error", "Please enter Customer Phone Number to send WhatsApp bill.")
            return
            
        if not self.current_invoice.items:
            messagebox.showerror("Error", "Invoice is empty. Add items first.")
            return

        # Ensure totals are up to date
        self.update_totals()

        # Format the bill text
        bill_text = f"*- -🧾 SMART RETAIL BILL 🧾- -*\n\n"
        bill_text += f"*Invoice ID:* {self.current_invoice.invoice_id}\n"
        customer = self.customer_name.get().strip()
        if customer:
            bill_text += f"*Customer:* {customer}\n"
        
        bill_text += "\n*--- Items ---*\n"
        for i, item in enumerate(self.current_invoice.items, 1):
            bill_text += f"{i}. {item.product_name}\n"
            bill_text += f"   {item.quantity} x ₹{item.unit_price:.2f} = ₹{item.line_total:.2f}\n"

        bill_text += "\n*--- Totals ---*\n"
        bill_text += f"Subtotal: ₹{self.current_invoice.subtotal:.2f}\n"
        if self.current_invoice.discount_amount > 0:
            bill_text += f"Discount: ₹{self.current_invoice.discount_amount:.2f}\n"
        bill_text += f"GST Amount: ₹{self.current_invoice.gst_amount:.2f}\n"
        bill_text += f"*GRAND TOTAL: ₹{self.current_invoice.grand_total:.2f}*\n"
        
        bill_text += f"\nPayment Mode: {self.payment_var.get()}\n"
        bill_text += "\n✅ _Thank you for shopping with us!_"

        import urllib.parse
        import webbrowser
        
        # Format phone number for WhatsApp
        if len(phone) == 10 and phone.isdigit():
            phone = "91" + phone
        elif phone.startswith("+"):
            phone = phone[1:]

        escaped_text = urllib.parse.quote(bill_text)
        url = f"https://wa.me/{phone}?text={escaped_text}"
        
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open browser: {str(e)}")

    def generate_pay_qr(self):
        """Generate and display dynamic UPI QR code"""
        if float(self.current_invoice.grand_total) <= 0:
            messagebox.showerror("Error", "Bill amount is 0. Add items first.")
            return

        try:
            import qrcode
            from PIL import Image, ImageTk
            import urllib.parse
            import tkinter as tk

            upi_id = "swadeeppatil@slc"
            merchant_name = urllib.parse.quote("Smart Retail")
            amount = f"{self.current_invoice.grand_total:.2f}"
            
            # UPI Deep Link formatting
            upi_link = f"upi://pay?pa={upi_id}&pn={merchant_name}&am={amount}&cu=INR"

            # Generate QR
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(upi_link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Create a popup window
            qr_window = tk.Toplevel(self.window)
            qr_window.title("Scan to Pay")
            qr_window.geometry("400x500")
            qr_window.configure(bg="white")
            qr_window.resizable(False, False)

            # Header
            ttk.Label(qr_window, text="💳 SCAN & PAY", font=("Arial", 18, "bold"), background="white").pack(pady=(20, 5))
            ttk.Label(qr_window, text=f"Total Amount: ₹{amount}", font=("Arial", 14, "bold"), foreground="#2ecc71", background="white").pack(pady=5)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            self._current_qr_image = photo  # prevent garbage collection
            
            qr_label = tk.Label(qr_window, image=photo, bg="white")
            qr_label.pack(pady=10)

            ttk.Label(qr_window, text=f"UPI ID: {upi_id}", font=("Arial", 10), background="white").pack(pady=5)
            
            pay_btn = ttk.Button(qr_window, text="Done (Close)", command=qr_window.destroy)
            pay_btn.pack(pady=15)

        except ImportError:
            messagebox.showerror("Dependency Error", "Please ensure 'qrcode' and 'pillow' libraries are installed.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate QR: {str(e)}")
