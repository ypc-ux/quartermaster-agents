#!/usr/bin/env python3
"""Analytics Agent — Quartermaster. Multi-source analytics, KPI tracking, performance dashboards."""

import json
from datetime import datetime, timedelta
from pathlib import Path

SOURCES = ["twitter", "website", "email", "sales", "social_media"]

KPI_CATEGORIES = {
    "growth": ["followers", "email_list", "revenue", "leads"],
    "engagement": ["likes", "comments", "shares", "click_through_rate", "reply_rate"],
    "conversion": ["signups", "purchases", "booked_calls", "demo_requests"],
    "retention": ["repeat_customers", "churn_rate", "lifetime_value"]
}

def track_kpis(kpis, timeframe="7d"):
    """Track KPIs across a timeframe."""
    tracked = []
    for kpi_name, value in kpis.items():
        tracked.append({
            "kpi": kpi_name,
            "value": value,
            "timeframe": timeframe,
            "tracked_at": datetime.now().isoformat(),
            "change_vs_previous": "[calculate delta]"
        })
    return {"type": "kpi_tracking", "kpis": tracked, "timeframe": timeframe}

def aggregate_sources(source_data):
    """Aggregate analytics from multiple sources."""
    aggregated = {
        "aggregated_at": datetime.now().isoformat(),
        "sources": [],
        "totals": {},
        "insights": []
    }
    for source_name, data in source_data.items():
        aggregated["sources"].append({
            "name": source_name,
            "metrics": data,
            "status": "connected"
        })
        for k, v in data.items():
            if k not in aggregated["totals"]:
                aggregated["totals"][k] = 0
            aggregated["totals"][k] += v
    return {"type": "aggregation", "data": aggregated}

def generate_dashboard(kpis, sources):
    """Generate a dashboard summary."""
    return {
        "generated_at": datetime.now().isoformat(),
        "period": "Last 7 days",
        "top_metrics": {k: v for k, v in list(kpis.items())[:5]},
        "source_count": len(sources),
        "health_score": 85,
        "alerts": [],
        "recommendations": ["Focus on conversion optimization", "Increase email engagement"]
    }

def run(kpis=None, sources=None):
    """Run analytics aggregation and dashboard generation."""
    kpis = kpis or {"followers": 14000, "revenue": 5000, "leads": 12, "email_list": 500}
    sources = sources or {s: {"visits": 100, "conversions": 5} for s in SOURCES}
    
    print(f"[Analytics Agent] Aggregating {len(sources)} sources...")
    agg = aggregate_sources(sources)
    tracked = track_kpis(kpis)
    dashboard = generate_dashboard(kpis, sources)
    
    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    
    result = {
        "aggregation": agg,
        "kpis": tracked,
        "dashboard": dashboard,
        "generated_at": datetime.now().isoformat()
    }
    
    out_path = out_dir / "analytics_report.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"[Analytics Agent] Dashboard generated:")
    print(f"  Sources: {len(sources)}")
    print(f"  KPIs tracked: {len(kpis)}")
    print(f"  Health score: {dashboard['health_score']}")
    return result

if __name__ == "__main__":
    run()
