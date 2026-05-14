"""Smart Discount Engine - Rule-based automatic discount system"""

from datetime import datetime
from typing import List, Optional


class DiscountRule:
    """A single discount rule"""
    def __init__(self, rule_id, name, rule_type, condition_value, discount_percent,
                 active=True, start_time=None, end_time=None):
        self.rule_id = rule_id
        self.name = name
        self.rule_type = rule_type  # 'min_qty', 'min_amount', 'happy_hour', 'category'
        self.condition_value = condition_value
        self.discount_percent = discount_percent
        self.active = active
        self.start_time = start_time  # HH:MM for happy_hour
        self.end_time = end_time


# Default built-in rules
DEFAULT_RULES = [
    DiscountRule("R1", "Buy 3+ items, get 5% off", "min_qty", 3, 5.0),
    DiscountRule("R2", "Buy 5+ items, get 10% off", "min_qty", 5, 10.0),
    DiscountRule("R3", "Spend ₹2000+, get 5% off", "min_amount", 2000, 5.0),
    DiscountRule("R4", "Spend ₹5000+, get 10% off", "min_amount", 5000, 10.0),
    DiscountRule("R5", "Happy Hour (2-4 PM): 15% off", "happy_hour", 0, 15.0,
                 start_time="14:00", end_time="16:00"),
    DiscountRule("R6", "Weekend Special: 8% off", "weekend", 0, 8.0),
]


class DiscountEngine:
    """Evaluates discount rules against invoices"""

    def __init__(self, rules: List[DiscountRule] = None):
        self.rules = rules or DEFAULT_RULES.copy()

    def evaluate(self, invoice) -> List[dict]:
        """Evaluate all active rules against an invoice.
        Returns list of applicable discounts with details.
        """
        applicable = []
        now = datetime.now()
        total_qty = sum(item.quantity for item in invoice.items)
        subtotal = sum(item.line_total for item in invoice.items)

        for rule in self.rules:
            if not rule.active:
                continue

            matched = False

            if rule.rule_type == "min_qty" and total_qty >= rule.condition_value:
                matched = True

            elif rule.rule_type == "min_amount" and subtotal >= rule.condition_value:
                matched = True

            elif rule.rule_type == "happy_hour" and rule.start_time and rule.end_time:
                current_time = now.strftime("%H:%M")
                if rule.start_time <= current_time <= rule.end_time:
                    matched = True

            elif rule.rule_type == "weekend" and now.weekday() >= 5:
                matched = True

            if matched:
                applicable.append({
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "discount_percent": rule.discount_percent,
                    "savings": subtotal * rule.discount_percent / 100,
                })

        return applicable

    def get_best_discount(self, invoice) -> Optional[dict]:
        """Get the highest applicable discount"""
        applicable = self.evaluate(invoice)
        if not applicable:
            return None
        return max(applicable, key=lambda x: x["discount_percent"])

    def get_all_rules(self) -> List[DiscountRule]:
        return self.rules

    def toggle_rule(self, rule_id, active):
        for r in self.rules:
            if r.rule_id == rule_id:
                r.active = active
                return True
        return False

    def add_rule(self, rule: DiscountRule):
        self.rules.append(rule)
