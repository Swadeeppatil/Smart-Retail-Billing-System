"""AI Demand Forecasting & ABC Analysis"""

from datetime import datetime, timedelta
from collections import defaultdict


class DemandForecaster:
    """Predict product demand using weighted moving average + ABC analysis"""

    def __init__(self, storage):
        self.storage = storage

    def forecast_demand(self, days_ahead=7, top_n=10):
        invoices = self.storage.get_all_invoices()
        products = self.storage.get_all_products()
        product_map = {p.product_id: p for p in products}
        today = datetime.now().date()
        product_daily = defaultdict(lambda: defaultdict(int))

        for inv in invoices:
            try:
                inv_date = datetime.fromisoformat(inv.created_at).date()
            except Exception:
                continue
            days_ago = (today - inv_date).days
            if 0 <= days_ago <= 30:
                for item in inv.items:
                    product_daily[item.product_id][days_ago] += item.quantity

        forecasts = []
        for pid, daily_sales in product_daily.items():
            product = product_map.get(pid)
            if not product:
                continue
            total_w, w_sum = 0, 0
            for d in range(31):
                w = max(1, 31 - d)
                w_sum += daily_sales.get(d, 0) * w
                total_w += w
            avg_daily = w_sum / total_w if total_w else 0
            predicted = round(avg_daily * days_ahead, 1)
            days_out = round(product.stock_quantity / avg_daily) if avg_daily > 0 else 999
            recent = sum(daily_sales.get(d, 0) for d in range(7)) / 7
            older = sum(daily_sales.get(d, 0) for d in range(7, 14)) / 7
            trend_pct = ((recent - older) / older * 100) if older > 0 else 0
            trend = "📈 Rising" if trend_pct > 10 else ("📉 Falling" if trend_pct < -10 else "➡️ Stable")

            forecasts.append({
                "product_name": product.name, "category": product.category,
                "current_stock": product.stock_quantity,
                "avg_daily": round(avg_daily, 2), "predicted": predicted,
                "days_stockout": days_out,
                "reorder": predicted > product.stock_quantity,
                "trend": trend, "trend_pct": round(trend_pct, 1),
                "reorder_qty": max(0, round(predicted - product.stock_quantity + avg_daily * 7)),
            })
        forecasts.sort(key=lambda x: (not x["reorder"], x["days_stockout"]))
        return forecasts[:top_n]

    def get_abc_analysis(self):
        invoices = self.storage.get_all_invoices()
        products = self.storage.get_all_products()
        product_map = {p.product_id: p for p in products}
        rev = defaultdict(float)
        for inv in invoices:
            for item in inv.items:
                rev[item.product_id] += item.line_total
        if not rev:
            return {"A": [], "B": [], "C": []}
        sorted_p = sorted(rev.items(), key=lambda x: x[1], reverse=True)
        total = sum(v for _, v in sorted_p)
        result = {"A": [], "B": [], "C": []}
        cum = 0
        for pid, r in sorted_p:
            p = product_map.get(pid)
            if not p:
                continue
            cum += r
            pct = cum / total * 100 if total else 0
            entry = {"name": p.name, "category": p.category, "revenue": round(r, 2),
                      "pct": round(r / total * 100, 1) if total else 0,
                      "cum_pct": round(pct, 1), "stock": p.stock_quantity}
            cls = "A" if pct <= 80 else ("B" if pct <= 95 else "C")
            entry["class"] = cls
            result[cls].append(entry)
        return result
