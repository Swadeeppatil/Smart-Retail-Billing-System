"""PDF Invoice generation"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import os
from models.models import Invoice


class InvoicePDF:
    """Generate PDF invoices"""

    def __init__(self, invoice_dir: str = "invoices"):
        self.invoice_dir = invoice_dir
        os.makedirs(invoice_dir, exist_ok=True)

    def generate_pdf(self, invoice: Invoice, company_name: str = "Smart Retail Billing") -> bool:
        """Generate PDF for invoice"""
        try:
            filename = os.path.join(self.invoice_dir, f"{invoice.invoice_id}.pdf")
            doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
            elements = []
            styles = getSampleStyleSheet()

            # Header
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=6,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            invoice_num_style = ParagraphStyle(
                'InvoiceNum',
                parent=styles['Normal'],
                fontSize=14,
                alignment=TA_CENTER,
                spaceAfter=12
            )

            elements.append(Paragraph(company_name, title_style))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(f"Invoice #{invoice.invoice_id}", invoice_num_style))
            elements.append(Spacer(1, 0.2*inch))

            # Invoice Details
            details_data = [
                ["Date:", datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "Payment Mode:", invoice.payment_mode],
                ["Customer:", invoice.customer_name, "Phone:", invoice.customer_phone or "N/A"],
                ["Cashier:", invoice.created_by, "", ""]
            ]
            
            details_table = Table(details_data, colWidths=[1.2*inch, 2*inch, 1.2*inch, 2*inch])
            details_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(details_table)
            elements.append(Spacer(1, 0.3*inch))

            # Items Table
            items_data = [["Item", "Qty", "Unit Price", "Discount %", "Amount"]]
            for item in invoice.items:
                items_data.append([
                    item.product_name[:20],
                    str(item.quantity),
                    f"₹{item.unit_price:.2f}",
                    f"{item.discount_percent}%",
                    f"₹{item.line_total:.2f}"
                ])

            items_table = Table(items_data, colWidths=[2.5*inch, 0.8*inch, 1.2*inch, 1*inch, 1*inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ]))
            elements.append(items_table)
            elements.append(Spacer(1, 0.2*inch))

            # Totals
            totals_data = [
                ["Subtotal:", f"₹{invoice.subtotal:.2f}"],
                ["Discount ({:.1f}%)".format(invoice.discount_percent), f"-₹{invoice.discount_amount:.2f}"],
                ["GST ({:.1f}%)".format(invoice.gst_percent), f"₹{invoice.gst_amount:.2f}"],
                ["GRAND TOTAL:", f"₹{invoice.grand_total:.2f}"],
            ]
            
            totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e0e0e0')),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ]))
            elements.append(totals_table)
            elements.append(Spacer(1, 0.3*inch))

            # Footer
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
            elements.append(Paragraph("Thank you for your purchase!", footer_style))
            elements.append(Paragraph("This is a computer-generated invoice", footer_style))

            # Build PDF
            doc.build(elements)
            return True
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False

    def get_invoice_path(self, invoice_id: str) -> str:
        """Get path to invoice PDF"""
        return os.path.join(self.invoice_dir, f"{invoice_id}.pdf")
