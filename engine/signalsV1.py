import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path

def calculate_signals(df):
    df["SMA_50"] = df["Adj Close"].rolling(window=50).mean()
    df["SMA_200"] = df["Adj Close"].rolling(window=200).mean()

    # Calculate RSI
    delta = df["Adj Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI_14"] = 100 - (100 / (1 + rs))

    # Calculate MACD and Signal Line
    ema_12 = df["Adj Close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["Adj Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema_12 - ema_26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    # --- Professional indicators (optional columns) ---
    # Calculate Bollinger Bands (20 period, 2 std)
    sma_20 = df["Adj Close"].rolling(window=20).mean()
    std_20 = df["Adj Close"].rolling(window=20).std()
    df["BB_Upper"] = sma_20 + (2 * std_20)
    df["BB_Mid"] = sma_20
    df["BB_Lower"] = sma_20 - (2 * std_20)

    # Calculate EMA 9 and EMA 21
    df["EMA_9"] = df["Adj Close"].ewm(span=9, adjust=False).mean()
    df["EMA_21"] = df["Adj Close"].ewm(span=21, adjust=False).mean()

    # Calculate ATR (Average True Range, 14 period)
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Adj Close"].shift()).abs()
    low_close = (df["Low"] - df["Adj Close"].shift()).abs()
    tr = high_low.to_frame(name="HL").join(high_close.rename("HC")).join(low_close.rename("LC")).max(axis=1)
    df["ATR_14"] = tr.rolling(window=14).mean()

    return df

def run():
    print("[✓] signals.py module initialized.")

    # Load portfolio tickers
    base_dir = Path(__file__).resolve().parents[1]
    portfolio_path = base_dir / "data" / "static" / "portfolio.json"
    with open(portfolio_path, "r") as f:
        portfolio_data = json.load(f)
    tickers = [pos["ticker"] for pos in portfolio_data.get("position_list", [])]

    # Define output directory
    signals_path = base_dir / "data" / "signals"
    signals_path.mkdir(parents=True, exist_ok=True)

    # Generate signals for each ticker
    for ticker in tickers:
        try:
            df = load_raw_data(ticker)
            df = calculate_signals(df)
            output_file = signals_path / f"{ticker}_signals.csv"
            df.to_csv(output_file)
            print(f"[✓] Saved signal data for {ticker} to {output_file}")
        except Exception as e:
            print(f"[X] Failed to generate signals for {ticker}: {e}")

def load_raw_data(ticker):
    raw_path = Path(__file__).resolve().parents[1] / "data" / "raw" / f"{ticker}.csv"
    df = pd.read_csv(raw_path, parse_dates=["Date"], index_col="Date")
    return df

if __name__ == "__main__":
    run()
