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

# Prepare output with last_updated timestamp
output = {
    "last_updated": datetime.utcnow().isoformat() + "Z",
    "positions": positions
}

# Save updated positions
with open(positions_file, 'w') as f:
    json.dump(output, f, indent=2)

print(f"Updated prices and alerts for {len(positions)} positions.")