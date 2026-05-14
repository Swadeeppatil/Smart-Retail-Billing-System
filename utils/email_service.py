"""Email service for sending invoices and reports"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import threading


class EmailService:
    """Send emails with PDF attachments (invoices, reports)"""

    # Default SMTP settings (Gmail)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = ""
    SENDER_PASSWORD = ""  # App Password, not regular password

    def __init__(self, sender_email="", sender_password="",
                 smtp_server="smtp.gmail.com", smtp_port=587):
        self.sender_email = sender_email or self.SENDER_EMAIL
        self.sender_password = sender_password or self.SENDER_PASSWORD
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def is_configured(self):
        return bool(self.sender_email and self.sender_password)

    def send_invoice_email(self, to_email, invoice, pdf_path, callback=None):
        """Send invoice PDF via email in background thread"""
        def _send():
            try:
                result = self._send_email(
                    to_email=to_email,
                    subject=f"Invoice {invoice.invoice_id} - Smart Retail",
                    body=self._format_invoice_body(invoice),
                    attachment_path=pdf_path
                )
                if callback:
                    callback(result, None)
            except Exception as e:
                if callback:
                    callback(False, str(e))

        threading.Thread(target=_send, daemon=True).start()

    def send_daily_summary(self, to_email, summary_text, callback=None):
        """Send daily sales summary email"""
        def _send():
            try:
                result = self._send_email(
                    to_email=to_email,
                    subject=f"Daily Sales Summary - Smart Retail",
                    body=summary_text
                )
                if callback:
                    callback(result, None)
            except Exception as e:
                if callback:
                    callback(False, str(e))

        threading.Thread(target=_send, daemon=True).start()

    def _send_email(self, to_email, subject, body, attachment_path=None):
        """Send an email with optional attachment"""
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                                f'attachment; filename={os.path.basename(attachment_path)}')
                msg.attach(part)

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
        return True

    def _format_invoice_body(self, invoice):
        items_html = ""
        for item in invoice.items:
            items_html += f"<tr><td>{item.product_name}</td><td>{item.quantity}</td><td>₹{item.unit_price:.2f}</td><td>₹{item.line_total:.2f}</td></tr>"

        return f"""
        <html><body style="font-family:Arial;color:#333">
        <h2 style="color:#007acc">🧾 Invoice {invoice.invoice_id}</h2>
        <p><strong>Customer:</strong> {invoice.customer_name}</p>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%">
        <tr style="background:#007acc;color:white"><th>Product</th><th>Qty</th><th>Price</th><th>Total</th></tr>
        {items_html}
        </table>
        <p><strong>Subtotal:</strong> ₹{invoice.subtotal:.2f}</p>
        <p><strong>GST ({invoice.gst_percent}%):</strong> ₹{invoice.gst_amount:.2f}</p>
        <h3 style="color:#27ae60">Grand Total: ₹{invoice.grand_total:.2f}</h3>
        <p>Payment: {invoice.payment_mode}</p>
        <hr><p style="color:#888;font-size:12px">Smart Retail Billing System | Auto-generated invoice</p>
        </body></html>
        """
