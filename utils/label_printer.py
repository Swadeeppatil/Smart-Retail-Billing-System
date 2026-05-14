"""Barcode Label Sheet Printer - Generate printable PDF sheets of barcode labels"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128

class LabelPrinter:
    """Generate PDF sheets with barcode labels (3 columns x 10 rows = 30 labels/page)"""
    COLS, ROWS = 3, 10
    LABEL_W, LABEL_H = 63.5*mm, 25.4*mm
    MARGIN_X, MARGIN_Y = 7*mm, 13*mm

    def __init__(self):
        os.makedirs("data/labels", exist_ok=True)

    def generate_label_sheet(self, products, filepath=None):
        if not filepath:
            filepath = "data/labels/barcode_labels.pdf"
        c = canvas.Canvas(filepath, pagesize=A4)
        pw, ph = A4
        idx = 0
        for p in products:
            col = idx % self.COLS
            row = (idx // self.COLS) % self.ROWS
            if idx > 0 and idx % (self.COLS * self.ROWS) == 0:
                c.showPage()
            x = self.MARGIN_X + col * self.LABEL_W
            y = ph - self.MARGIN_Y - (row + 1) * self.LABEL_H
            # Draw label
            c.setFont("Helvetica-Bold", 7)
            c.drawString(x + 2*mm, y + self.LABEL_H - 5*mm, p.name[:25])
            c.setFont("Helvetica", 6)
            c.drawString(x + 2*mm, y + self.LABEL_H - 9*mm, f"MRP: Rs.{p.selling_price:.0f}")
            try:
                bc = code128.Code128(p.barcode, barWidth=0.5*mm, barHeight=8*mm)
                bc.drawOn(c, x + 2*mm, y + 2*mm)
            except:
                c.drawString(x + 2*mm, y + 4*mm, p.barcode)
            c.setFont("Helvetica", 5)
            c.drawString(x + 2*mm, y + 1*mm, p.barcode)
            idx += 1
        c.save()
        return filepath
