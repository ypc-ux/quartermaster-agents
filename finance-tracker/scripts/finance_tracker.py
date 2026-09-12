#!/usr/bin/env python3
"""Finance Tracker — Quartermaster. Track revenue, expenses, and financial KPIs."""

import json
from datetime import datetime, timedelta
from pathlib import Path

CATEGORIES = {
    "revenue": ["services", "products", "subscriptions", "consulting", "other"],
    "expenses": ["tools", "marketing", "contractors", "hosting", "other"]
}

def log_transaction(amount, category, description, transaction_type="revenue"):
    """Log a financial transaction."""
    return {
        "id": f"txn_{int(datetime.now().timestamp())}",
        "amount": amount,
        "category": category,
        "description": description,
        "type": transaction_type,
        "date": datetime.now().isoformat(),
        "status": "recorded"
    }

def calculate_metrics(transactions, period="30d"):
    """Calculate financial metrics from transactions."""
    revenues = [t["amount"] for t in transactions if t["type"] == "revenue"]
    expenses = [t["amount"] for t in transactions if t["type"] == "expense"]
    
    total_revenue = sum(revenues)
    total_expenses = sum(expenses)
    net_profit = total_revenue - total_expenses
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return {
        "period": period,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "profit_margin_pct": round(profit_margin, 2),
        "transaction_count": len(transactions),
        "revenue_by_category": {cat: sum(t["amount"] for t in transactions if t["type"] == "revenue" and t["category"] == cat) for cat in CATEGORIES["revenue"]},
        "expenses_by_category": {cat: sum(t["amount"] for t in transactions if t["type"] == "expense" and t["category"] == cat) for cat in CATEGORIES["expenses"]}
    }

def run():
    """Demo: log sample transactions and calculate metrics."""
    print("[Finance Tracker] Logging sample transactions...")
    
    transactions = [
        log_transaction(5000, "services", "Website build for client A", "revenue"),
        log_transaction(1500, "subscriptions", "Monthly retainer client B", "revenue"),
        log_transaction(200, "tools", "Software subscriptions", "expense"),
        log_transaction(800, "marketing", "Ad spend", "expense"),
        log_transaction(3000, "consulting", "Strategy session client C", "revenue"),
    ]
    
    metrics = calculate_metrics(transactions)
    
    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    
    result = {
        "transactions": transactions,
        "metrics": metrics,
        "updated_at": datetime.now().isoformat()
    }
    
    out_path = out_dir / "finance.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"[Finance Tracker] Financial summary:")
    print(f"  Revenue: ${metrics['total_revenue']:,}")
    print(f"  Expenses: ${metrics['total_expenses']:,}")
    print(f"  Net profit: ${metrics['net_profit']:,}")
    print(f"  Margin: {metrics['profit_margin_pct']}%")
    print(f"  Transactions: {metrics['transaction_count']}")
    print(f"  Saved to: {out_path}")
    return result

if __name__ == "__main__":
    run()
