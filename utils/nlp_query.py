"""Natural Language Query Engine - Ask questions about your data in plain English"""

import re
from datetime import datetime, timedelta


class NLPQueryEngine:
    """Parse natural language questions and return answers from the database"""

    def __init__(self, storage):
        self.storage = storage

    def query(self, text: str) -> str:
        """Process a natural language query and return an answer"""
        text = text.lower().strip()

        # Route to handler
        handlers = [
            (r'(top|best)\s*(\d+)?\s*(sell|product|item)', self._top_products),
            (r'(profit|earning).*?(today|yesterday|this week|last week|this month|last month|\d{4}-\d{2}-\d{2})', self._profit_query),
            (r'(revenue|sales|sale).*?(today|yesterday|this week|last week|this month|\d{4}-\d{2}-\d{2})', self._revenue_query),
            (r'(how many|total|count)\s*(invoice|bill)', self._invoice_count),
            (r'(expir|expiry).*?(\d+)?\s*(day|week|month)', self._expiring_products),
            (r'(low stock|out of stock|stock.*low)', self._low_stock),
            (r'(total|how many)\s*(product|item)', self._product_count),
            (r'(most expensive|costliest|highest price)', self._most_expensive),
            (r'(cheapest|lowest price|least expensive)', self._cheapest),
            (r'(average|avg).*?(invoice|bill|sale)', self._avg_invoice),
            (r'(category|categories)', self._categories),
            (r'(stock value|inventory value|total stock)', self._stock_value),
            (r'help|what can you|commands', self._help),
        ]

        for pattern, handler in handlers:
            match = re.search(pattern, text)
            if match:
                return handler(text, match)

        return self._help(text, None)

    def _parse_date_range(self, text):
        today = datetime.now().date()
        if 'today' in text:
            return today.isoformat(), today.isoformat()
        if 'yesterday' in text:
            d = today - timedelta(days=1)
            return d.isoformat(), d.isoformat()
        if 'this week' in text:
            start = today - timedelta(days=today.weekday())
            return start.isoformat(), today.isoformat()
        if 'last week' in text:
            start = today - timedelta(days=today.weekday() + 7)
            end = start + timedelta(days=6)
            return start.isoformat(), end.isoformat()
        if 'this month' in text:
            return today.replace(day=1).isoformat(), today.isoformat()
        if 'last month' in text:
            first = today.replace(day=1)
            last_m_end = first - timedelta(days=1)
            last_m_start = last_m_end.replace(day=1)
            return last_m_start.isoformat(), last_m_end.isoformat()
        # Default: last 30 days
        return (today - timedelta(days=30)).isoformat(), today.isoformat()

    def _top_products(self, text, match):
        n = int(match.group(2)) if match.group(2) else 5
        invoices = self.storage.get_all_invoices()
        sales = {}
        for inv in invoices:
            for item in inv.items:
                sales[item.product_name] = sales.get(item.product_name, 0) + item.quantity
        if not sales:
            return "📊 No sales data yet."
        top = sorted(sales.items(), key=lambda x: x[1], reverse=True)[:n]
        lines = [f"  {i+1}. {name} — {qty} units sold" for i, (name, qty) in enumerate(top)]
        return f"🏆 Top {n} Selling Products:\n" + "\n".join(lines)

    def _revenue_query(self, text, match):
        start, end = self._parse_date_range(text)
        invoices = self.storage.get_all_invoices()
        filtered = [i for i in invoices if start <= i.created_at[:10] <= end]
        total = sum(i.grand_total for i in filtered)
        return f"💰 Revenue ({start} to {end}):\n  ₹{total:,.2f} from {len(filtered)} invoices"

    def _profit_query(self, text, match):
        start, end = self._parse_date_range(text)
        invoices = self.storage.get_all_invoices()
        products = self.storage.get_all_products()
        cost_map = {p.product_id: p.cost_price for p in products}
        filtered = [i for i in invoices if start <= i.created_at[:10] <= end]
        revenue = sum(i.grand_total for i in filtered)
        cogs = sum(cost_map.get(item.product_id, 0) * item.quantity
                    for inv in filtered for item in inv.items)
        profit = revenue - cogs
        return f"📈 Profit ({start} to {end}):\n  Revenue: ₹{revenue:,.2f}\n  Cost: ₹{cogs:,.2f}\n  Profit: ₹{profit:,.2f}"

    def _invoice_count(self, text, match):
        start, end = self._parse_date_range(text)
        invoices = self.storage.get_all_invoices()
        filtered = [i for i in invoices if start <= i.created_at[:10] <= end]
        return f"🧾 Invoice Count ({start} to {end}): {len(filtered)}"

    def _expiring_products(self, text, match):
        days = int(match.group(2)) if match.group(2) else 30
        products = self.storage.get_all_products()
        today = datetime.now().date()
        limit = today + timedelta(days=days)
        expiring = []
        for p in products:
            if p.expiry_date:
                for fmt in ('%Y-%m-%d', '%d-%m-%Y'):
                    try:
                        ed = datetime.strptime(p.expiry_date.strip(), fmt).date()
                        if ed <= limit:
                            expiring.append((p.name, ed))
                        break
                    except ValueError:
                        continue
        if not expiring:
            return f"✅ No products expiring within {days} days."
        lines = [f"  ⚠️ {name} — expires {d}" for name, d in sorted(expiring, key=lambda x: x[1])]
        return f"📅 Products expiring within {days} days ({len(expiring)}):\n" + "\n".join(lines[:10])

    def _low_stock(self, text, match):
        products = self.storage.get_all_products()
        low = [p for p in products if p.stock_quantity <= 10]
        if not low:
            return "✅ All products have sufficient stock."
        low.sort(key=lambda p: p.stock_quantity)
        lines = [f"  📦 {p.name} — {p.stock_quantity} left" for p in low[:10]]
        return f"⚠️ Low Stock Products ({len(low)}):\n" + "\n".join(lines)

    def _product_count(self, text, match):
        products = self.storage.get_all_products()
        return f"📦 Total Products: {len(products)}"

    def _most_expensive(self, text, match):
        products = self.storage.get_all_products()
        if not products:
            return "No products found."
        top = sorted(products, key=lambda p: p.selling_price, reverse=True)[:5]
        lines = [f"  {p.name} — ₹{p.selling_price:.2f}" for p in top]
        return "💎 Most Expensive Products:\n" + "\n".join(lines)

    def _cheapest(self, text, match):
        products = self.storage.get_all_products()
        if not products:
            return "No products found."
        top = sorted(products, key=lambda p: p.selling_price)[:5]
        lines = [f"  {p.name} — ₹{p.selling_price:.2f}" for p in top]
        return "🏷️ Cheapest Products:\n" + "\n".join(lines)

    def _avg_invoice(self, text, match):
        invoices = self.storage.get_all_invoices()
        if not invoices:
            return "No invoices yet."
        avg = sum(i.grand_total for i in invoices) / len(invoices)
        return f"📊 Average Invoice Value: ₹{avg:,.2f} (from {len(invoices)} invoices)"

    def _categories(self, text, match):
        products = self.storage.get_all_products()
        cats = {}
        for p in products:
            cats[p.category] = cats.get(p.category, 0) + 1
        lines = [f"  {cat}: {count} products" for cat, count in sorted(cats.items())]
        return "📂 Categories:\n" + "\n".join(lines)

    def _stock_value(self, text, match):
        products = self.storage.get_all_products()
        cost_val = sum(p.cost_price * p.stock_quantity for p in products)
        sell_val = sum(p.selling_price * p.stock_quantity for p in products)
        return f"🏪 Inventory Value:\n  At Cost: ₹{cost_val:,.2f}\n  At Selling Price: ₹{sell_val:,.2f}\n  Potential Profit: ₹{sell_val - cost_val:,.2f}"

    def _help(self, text, match):
        return """💬 Ask me anything! Example queries:

• "Top 5 selling products"
• "Revenue today" / "Sales this week"
• "Profit last month"
• "How many invoices this month"
• "Products expiring in 7 days"
• "Low stock products"
• "Total products"
• "Most expensive product"
• "Average invoice value"
• "Stock value"
• "Categories"
"""
