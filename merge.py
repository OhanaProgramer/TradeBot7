import json
from pathlib import Path

# Set paths
base_path = Path(__file__).parent / "data"
checklist_file = base_path / "dailyChecklist.json"
strategy_file = base_path / "strategy.json"
output_file = base_path / "positions.json"

# Load data
with open(checklist_file, 'r') as f:
    daily_data = json.load(f)
with open(strategy_file, 'r') as f:
    strategy_data = json.load(f)

# Create dictionary for strategy.json
strategy_dict = {item['ticker']: item for item in strategy_data}

merged_positions = []

for ticker, info in daily_data.items():
    strat = strategy_dict.get(ticker, {})
    merged_positions.append({
        "ticker": ticker,
        "price": strat.get("price"),
        "position_qty": strat.get("position_qty"),
        "cost_basis": strat.get("cost_basis"),
        "trend": strat.get("trend"),
        "support_levels": strat.get("support_levels", []),
        "resistance_levels": strat.get("resistance_levels", []),
        "indicators": strat.get("indicators", {}),
        "action_plan": {
            "narrative": strat.get("today_signal", info.get("action")),
            "stop_loss": strat.get("stop_loss"),
            "stop_type": strat.get("stop_type"),
            "trailing_stop_pct": strat.get("trailing_stop_pct")
        },
        "alerts": {
            "stop_near": False,
            "volatility": "normal",
            "attention": "none"
        }
    })

# Include tickers in strategy.json not in dailyChecklist
for ticker, strat in strategy_dict.items():
    if ticker not in daily_data:
        merged_positions.append({
            "ticker": ticker,
            "price": strat.get("price"),
            "position_qty": strat.get("position_qty"),
            "cost_basis": strat.get("cost_basis"),
            "trend": strat.get("trend"),
            "support_levels": strat.get("support_levels", []),
            "resistance_levels": strat.get("resistance_levels", []),
            "indicators": strat.get("indicators", {}),
            "action_plan": {
                "narrative": strat.get("today_signal"),
                "stop_loss": strat.get("stop_loss"),
                "stop_type": strat.get("stop_type"),
                "trailing_stop_pct": strat.get("trailing_stop_pct")
            },
            "alerts": {
                "stop_near": False,
                "volatility": "normal",
                "attention": "none"
            }
        })

# Write merged results
with open(output_file, 'w') as f:
    json.dump(merged_positions, f, indent=2)

print(f"Merged {len(merged_positions)} positions into {output_file}")
