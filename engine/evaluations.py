

import pandas as pd
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
SIGNALS_DIR = BASE_DIR / "data" / "signals"
PORTFOLIO_PATH = BASE_DIR / "data" / "static" / "portfolio.json"

def load_portfolio():
    with open(PORTFOLIO_PATH, "r") as f:
        return json.load(f)["position_list"]

def load_signals(ticker):
    path = SIGNALS_DIR / f"{ticker}_signals.csv"
    return pd.read_csv(path, parse_dates=["Date"], index_col="Date")

def interpret_signals(latest, strategy):
    rsi_signal = macd_signal = sma_signal = "Neutral"

    # RSI evaluation
    if strategy.get("use_rsi", False):
        if latest["RSI_14"] < strategy.get("rsi_buy", 30):
            rsi_signal = "Bullish"
        elif latest["RSI_14"] > strategy.get("rsi_sell", 70):
            rsi_signal = "Bearish"

    # MACD evaluation
    if strategy.get("use_macd", False):
        if latest["MACD"] > latest["MACD_Signal"]:
            macd_signal = "Bullish"
        elif latest["MACD"] < latest["MACD_Signal"]:
            macd_signal = "Bearish"

    # SMA evaluation
    if strategy.get("use_sma", False):
        if latest["SMA_50"] > latest["SMA_200"]:
            sma_signal = "Bullish"
        else:
            sma_signal = "Bearish"

    return rsi_signal, macd_signal, sma_signal

def generate_recommendation(rsi_signal, macd_signal, sma_signal):
    signals = [rsi_signal, macd_signal, sma_signal]
    bullish_count = signals.count("Bullish")
    bearish_count = signals.count("Bearish")

    if bullish_count > bearish_count:
        return "Buy/Hold"
    elif bearish_count > bullish_count:
        return "Sell"
    return "Neutral/Hold"

def evaluate_position(position):
    ticker = position["ticker"]
    strategy = position.get("strategy", {})
    df = load_signals(ticker)
    latest = df.iloc[-1]

    rsi_signal, macd_signal, sma_signal = interpret_signals(latest, strategy)
    recommendation = generate_recommendation(rsi_signal, macd_signal, sma_signal)

    profile = {
        "ticker": ticker,
        "qty": position["qty"],
        "cost_basis": position["cost_basis"],
        "latest_price": latest["Adj Close"],
        "signals": {
            "rsi": rsi_signal,
            "macd": macd_signal,
            "sma": sma_signal
        },
        "recommendation": recommendation,
        "notes": strategy.get("notes", "")
    }
    return profile


# Save evaluation profile to disk (latest and timestamped historical)
def save_profile(profile):
    eval_dir = BASE_DIR / "data" / "evaluations"
    eval_dir.mkdir(parents=True, exist_ok=True)

    # Save latest profile
    latest_path = eval_dir / f"{profile['ticker']}_evaluation.json"
    with open(latest_path, "w") as f:
        json.dump(profile, f, indent=2)

    # Save a timestamped version for historical tracking
    timestamp = pd.Timestamp.now().strftime("%Y-%m-%d")
    history_path = eval_dir / f"{profile['ticker']}_{timestamp}.json"
    with open(history_path, "w") as f:
        json.dump(profile, f, indent=2)

    print(f"[✓] Saved evaluation for {profile['ticker']} to {latest_path} and history archive.")

def run():
    portfolio = load_portfolio()
    for pos in portfolio:
        profile = evaluate_position(pos)
        print(json.dumps(profile, indent=2))
        save_profile(profile)

if __name__ == "__main__":
    run()