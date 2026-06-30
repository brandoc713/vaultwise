from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import Category


@dataclass(frozen=True)
class CategoryDecision:
    category_id: uuid.UUID | None
    confidence: float
    source: str


RULES: list[tuple[list[str], str, float]] = [
    (["payroll", "direct deposit", "deposit"], "Income", 0.94),
    (["rent", "mortgage", "homes"], "Housing", 0.94),
    (["kroger", "grocery", "wholefds", "whole foods", "trader joe"], "Groceries", 0.9),
    (["energy", "utility", "water", "internet", "fibernet"], "Utilities", 0.9),
    (["ach transfer", "card payment", "credit card payment", "transfer"], "Transfers", 0.93),
    (["loan", "auto finance"], "Loans", 0.88),
    (["brokerage", "investment", "contribution"], "Investments", 0.88),
    (["fee", "maintenance"], "Fees", 0.86),
    (["cafe", "pizza", "restaurant"], "Dining", 0.82),
    (["shell", "uber", "parking", "gas"], "Transportation", 0.82),
    (["amazon", "target"], "Shopping", 0.72),
    (["cvs", "pharmacy", "hospital"], "Health", 0.78),
]


def categorize(description: str, merchant: str | None, db: Session) -> CategoryDecision:
    haystack = f"{description} {merchant or ''}".lower()
    categories = {category.name.lower(): category for category in db.query(Category).all()}
    for keywords, category_name, confidence in RULES:
        if any(keyword in haystack for keyword in keywords):
            category = categories.get(category_name.lower())
            return CategoryDecision(category.id if category else None, confidence, "rule")
    return CategoryDecision(None, 0.0, "none")
