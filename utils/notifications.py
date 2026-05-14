"""Desktop notification system using plyer/win10toast"""

import threading


class NotificationManager:
    """Send desktop toast notifications"""

    def __init__(self, app_name="Smart Retail Billing"):
        self.app_name = app_name
        self._backend = None
        self._detect_backend()

    def _detect_backend(self):
        try:
            from plyer import notification
            self._backend = "plyer"
        except ImportError:
            try:
                from win10toast import ToastNotifier
                self._backend = "win10toast"
                self._toaster = ToastNotifier()
            except ImportError:
                self._backend = None

    def notify(self, title, message, timeout=5):
        """Send a desktop notification (non-blocking)"""
        threading.Thread(target=self._send, args=(title, message, timeout),
                         daemon=True).start()

    def _send(self, title, message, timeout):
        try:
            if self._backend == "plyer":
                from plyer import notification
                notification.notify(
                    title=title, message=message,
                    app_name=self.app_name, timeout=timeout
                )
            elif self._backend == "win10toast":
                self._toaster.show_toast(title, message,
                                          duration=timeout, threaded=False)
            else:
                # Fallback: system beep
                import winsound
                winsound.MessageBeep()
        except Exception:
            pass

    def notify_low_stock(self, product_name, qty):
        self.notify("📦 Low Stock Alert",
                     f"{product_name} has only {qty} left!")

    def notify_expired(self, product_name):
        self.notify("❌ Product Expired",
                     f"{product_name} has expired! Remove from shelf.")

    def notify_invoice_saved(self, invoice_id, total):
        self.notify("✅ Invoice Saved",
                     f"Invoice {invoice_id} saved - ₹{total:.2f}")

    def notify_backup_complete(self):
        self.notify("💾 Backup Complete",
                     "Database backup created successfully.")
