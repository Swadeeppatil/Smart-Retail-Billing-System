"""GST Return Report Generator"""

from datetime import datetime
from collections import defaultdict
import csv
import os


class GSTReportGenerator:
    """Generate GSTR-1 format reports from invoices"""

    GST_SLABS = [0, 5, 12, 18, 28]

    def __init__(self, storage):
        self.storage = storage

    def generate_gstr1_data(self, from_date=None, to_date=None):
        """Generate GSTR-1 summary data"""
        invoices = self.storage.get_all_invoices()
        if from_date:
            invoices = [i for i in invoices if i.created_at[:10] >= from_date]
        if to_date:
            invoices = [i for i in invoices if i.created_at[:10] <= to_date]

        b2c_sales = []  # B2C (consumer) sales
        tax_summary = defaultdict(lambda: {"taxable": 0, "cgst": 0, "sgst": 0, "total_tax": 0, "count": 0})

        for inv in invoices:
            gst_rate = inv.gst_percent
            taxable = inv.subtotal - inv.discount_amount
            cgst = inv.gst_amount / 2
            sgst = inv.gst_amount / 2

            b2c_sales.append({
                "invoice_id": inv.invoice_id,
                "date": inv.created_at[:10],
                "customer": inv.customer_name,
                "taxable_value": round(taxable, 2),
                "gst_rate": gst_rate,
                "cgst": round(cgst, 2),
                "sgst": round(sgst, 2),
                "total": round(inv.grand_total, 2),
            })

            slab = str(int(gst_rate))
            tax_summary[slab]["taxable"] += taxable
            tax_summary[slab]["cgst"] += cgst
            tax_summary[slab]["sgst"] += sgst
            tax_summary[slab]["total_tax"] += inv.gst_amount
            tax_summary[slab]["count"] += 1

        # Overall summary
        total_taxable = sum(s["taxable"] for s in tax_summary.values())
        total_cgst = sum(s["cgst"] for s in tax_summary.values())
        total_sgst = sum(s["sgst"] for s in tax_summary.values())
        total_tax = sum(s["total_tax"] for s in tax_summary.values())
        total_invoices = len(invoices)
        total_revenue = sum(inv.grand_total for inv in invoices)

        return {
            "b2c_sales": b2c_sales,
            "tax_summary": dict(tax_summary),
            "overall": {
                "total_invoices": total_invoices,
                "total_taxable": round(total_taxable, 2),
                "total_cgst": round(total_cgst, 2),
                "total_sgst": round(total_sgst, 2),
                "total_tax": round(total_tax, 2),
                "total_revenue": round(total_revenue, 2),
            }
        }

    def export_gstr1_csv(self, filepath, from_date=None, to_date=None):
        """Export GSTR-1 data to CSV"""
        data = self.generate_gstr1_data(from_date, to_date)
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["GSTR-1 B2C Sales Report"])
                writer.writerow(["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M")])
                writer.writerow([])
                writer.writerow(["Invoice ID", "Date", "Customer", "Taxable Value",
                                 "GST Rate %", "CGST", "SGST", "Total"])
                for row in data["b2c_sales"]:
                    writer.writerow([row["invoice_id"], row["date"], row["customer"],
                                     row["taxable_value"], row["gst_rate"],
                                     row["cgst"], row["sgst"], row["total"]])
                writer.writerow([])
                writer.writerow(["Tax Summary by Slab"])
                writer.writerow(["GST Slab %", "Taxable Value", "CGST", "SGST", "Total Tax", "Invoice Count"])
                for slab, vals in data["tax_summary"].items():
                    writer.writerow([slab, round(vals["taxable"], 2), round(vals["cgst"], 2),
                                     round(vals["sgst"], 2), round(vals["total_tax"], 2), vals["count"]])
                writer.writerow([])
                o = data["overall"]
                writer.writerow(["Overall Summary"])
                writer.writerow(["Total Invoices", o["total_invoices"]])
                writer.writerow(["Total Taxable", o["total_taxable"]])
                writer.writerow(["Total CGST", o["total_cgst"]])
                writer.writerow(["Total SGST", o["total_sgst"]])
                writer.writerow(["Total Tax", o["total_tax"]])
                writer.writerow(["Total Revenue", o["total_revenue"]])
            return True
        except Exception as e:
            print(f"GST export error: {e}")
            return False
