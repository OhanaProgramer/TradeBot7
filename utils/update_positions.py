import json
import yfinance as yf
from pathlib import Path
from datetime import datetime

# Paths
base_path = Path(__file__).resolve().parents[1] / "data"
positions_file = base_path / "positions.json"

# Load existing positions (handle nested structure)
with open(positions_file, 'r') as f:
    data = json.load(f)
    positions = data["positions"] if isinstance(data, dict) and "positions" in data else data

def calculate_alerts(item):
    """Simple alert calculations based on price and stop."""
    price = item.get("price")
    stop_loss = item.get("action_plan", {}).get("stop_loss")
    rsi = item.get("indicators", {}).get("RSI")
    narrative = item.get("narrative", "").lower() if item.get("narrative") else ""

    alerts = {
        "stop_near": False,
        "volatility": "normal",
        "attention": "none",
        "category": "info",
        "message": ""
    }

    # Stop proximity alert
    if price and stop_loss:
        try:
            if abs(price - stop_loss) / stop_loss < 0.03:
                alerts["stop_near"] = True
        except ZeroDivisionError:
            pass

    # Volatility alert based on RSI
    if rsi is not None:
        if rsi > 70 or rsi < 30:
            alerts["volatility"] = "high"

    # Attention flag
    if alerts["stop_near"] and item.get("trend", "").lower().startswith("bearish"):
        alerts["attention"] = "critical"

    # Enhanced category detection based on trend, volatility, and narrative
    narrative_keywords_positive = ["breakout", "uptrend", "momentum", "bullish", "strong buy", "rally"]
    narrative_keywords_caution = ["watch", "resistance", "overbought", "volatile"]
    narrative_keywords_critical = ["stop", "exit", "sell-off", "bearish"]

    # Use narrative from action_plan if present, else fallback to narrative
    narrative_text = item.get("action_plan", {}).get("narrative", "")
    if not narrative_text:
        narrative_text = item.get("narrative", "")
    narrative_text = narrative_text.lower()

    if alerts["attention"] == "critical" or any(word in narrative_text for word in narrative_keywords_critical):
        alerts["category"] = "critical"
    elif any(word in narrative_text for word in narrative_keywords_positive) or item.get("trend", "").lower() == "bullish":
        alerts["category"] = "positive"
    elif alerts["volatility"] == "high" or any(word in narrative_text for word in narrative_keywords_caution):
        alerts["category"] = "caution"
    else:
        alerts["category"] = "info"

    # Compose message summarizing the alert
    messages = []
    if alerts["stop_near"]:
        messages.append("Price near stop loss")
    if alerts["volatility"] == "high":
        messages.append("High volatility indicated by RSI")
    if alerts["attention"] == "critical":
        messages.append("Critical attention: Bearish trend near stop")
    if not messages and alerts["category"] == "positive":
        messages.append("Positive outlook based on narrative")
    if not messages:
        messages.append("No significant alerts")

    alerts["message"] = "; ".join(messages)

    return alerts

# Update prices and alerts
for item in positions:
    ticker = item["ticker"]
    try:
        ticker_data = yf.Ticker(ticker)
        latest_price = ticker_data.history(period="1d")["Close"].iloc[-1]
        item["price"] = round(float(latest_price), 2)
        # Fetch previous close and calculate daily changes
        try:
            prev_close = ticker_data.history(period="2d")["Close"].iloc[-2]
            item["previous_close"] = round(float(prev_close), 2)
            item["daily_change"] = round(item["price"] - item["previous_close"], 2)
            item["daily_change_percent"] = round((item["daily_change"] / item["previous_close"]) * 100, 2) if item["previous_close"] else 0.0
        except Exception as e:
            item["previous_close"] = None
            item["daily_change"] = None
            item["daily_change_percent"] = None
    except Exception as e:
        print(f"Warning: Could not fetch price for {ticker}: {e}")
        item["previous_close"] = None
        item["daily_change"] = None
        item["daily_change_percent"] = None

    # Recalculate alerts
    item["alerts"] = calculate_alerts(item)


# Portfolio summary metrics
def compute_portfolio_summary(positions):
    total_value = 0.0
    total_invested = 0.0
    winners = []
    losers = []
    alert_counts = {
        "critical": 0,
        "caution": 0,
        "positive": 0,
        "info": 0
    }
    for item in positions:
        price = item.get("price")
        qty = item.get("position_qty", 0)
        cost_basis = item.get("cost_basis", 0)
        # Defensive: skip if price or cost_basis missing
        try:
            value = float(price) * float(qty)
            invested = float(cost_basis)
        except Exception:
            value = 0.0
            invested = 0.0
        total_value += value
        total_invested += invested
        # Compute % change for winner/loser lists
        try:
            pl_pct = ((float(price) - float(cost_basis)/float(qty)) / (float(cost_basis)/float(qty))) * 100 if qty != 0 else 0
        except Exception:
            pl_pct = 0
        # Use cost_basis > 0 and qty > 0 as filter
        if invested > 0 and qty > 0:
            winners.append({
                "ticker": item.get("ticker"),
                "pl_percent": pl_pct,
                "price": price,
                "cost_basis": cost_basis,
                "position_qty": qty
            })
        # Count alerts by category
        category = item.get("alerts", {}).get("category", "info")
        if category in alert_counts:
            alert_counts[category] += 1
        else:
            alert_counts["info"] += 1
    # Sort by pl_percent descending for winners, ascending for losers
    winners_sorted = sorted(winners, key=lambda x: x["pl_percent"], reverse=True)
    losers_sorted = sorted(winners, key=lambda x: x["pl_percent"])
    summary = {
        "total_value": round(total_value, 2),
        "total_invested": round(total_invested, 2),
        "total_pl_percent": round(((total_value - total_invested) / total_invested) * 100, 2) if total_invested else 0.0,
        "top_winners": winners_sorted[:3],
        "top_losers": losers_sorted[:3],
        "alert_counts": alert_counts
    }
    return summary

# Prepare output with last_updated timestamp in format 'Wed, Jul 30, 2025 – 13:52'
def format_last_updated(dt):
    # Example: Wed, Jul 30, 2025 – 13:52
    return dt.strftime("%a, %b %d, %Y – %H:%M")

meta_section = {
    "last_updated": format_last_updated(datetime.utcnow()),
    "portfolio_summary": compute_portfolio_summary(positions),
    "benchmark": {
        "symbol": "SPY",
        "current_price": None,
        "previous_close": None,
        "daily_change_percent": None,
        "ytd_change_percent": None
    }
}

output = {
    "meta": meta_section,
    "positions": positions
}

# Save updated positions
with open(positions_file, 'w') as f:
    json.dump(output, f, indent=2)

print(f"Updated prices and alerts for {len(positions)} positions.")