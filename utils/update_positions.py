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

    alerts = {
        "stop_near": False,
        "volatility": "normal",
        "attention": "none"
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

    return alerts

# Update prices and alerts
for item in positions:
    ticker = item["ticker"]
    try:
        ticker_data = yf.Ticker(ticker)
        latest_price = ticker_data.history(period="1d")["Close"].iloc[-1]
        item["price"] = round(float(latest_price), 2)
    except Exception as e:
        print(f"Warning: Could not fetch price for {ticker}: {e}")

    # Recalculate alerts
    item["alerts"] = calculate_alerts(item)


# Portfolio summary metrics
def compute_portfolio_summary(positions):
    total_value = 0.0
    total_invested = 0.0
    winners = []
    losers = []
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
    # Sort by pl_percent descending for winners, ascending for losers
    winners_sorted = sorted(winners, key=lambda x: x["pl_percent"], reverse=True)
    losers_sorted = sorted(winners, key=lambda x: x["pl_percent"])
    summary = {
        "total_value": round(total_value, 2),
        "total_invested": round(total_invested, 2),
        "total_pl_percent": round(((total_value - total_invested) / total_invested) * 100, 2) if total_invested else 0.0,
        "top_winners": winners_sorted[:3],
        "top_losers": losers_sorted[:3]
    }
    return summary

# Prepare output with last_updated timestamp in format 'Wed, Jul 30, 2025 – 13:52'
def format_last_updated(dt):
    # Example: Wed, Jul 30, 2025 – 13:52
    return dt.strftime("%a, %b %d, %Y – %H:%M")

output = {
    "last_updated": format_last_updated(datetime.utcnow()),
    "positions": positions,
    "portfolio_summary": compute_portfolio_summary(positions)
}

# Save updated positions
with open(positions_file, 'w') as f:
    json.dump(output, f, indent=2)

print(f"Updated prices and alerts for {len(positions)} positions.")