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

    return df

def run():
    ticker = "AAPL"
    print("[✓] signals.py module initialized.")
    df = load_raw_data(ticker)
    df = calculate_signals(df)
    # Save the signals DataFrame
    signals_path = Path(__file__).resolve().parents[1] / "data" / "signals"
    signals_path.mkdir(parents=True, exist_ok=True)
    output_file = signals_path / f"{ticker}_signals.csv"
    df.to_csv(output_file)
    print(f"[✓] Saved signal data for {ticker} to {output_file}")
    print(df[["Adj Close", "SMA_50", "SMA_200", "RSI_14", "MACD", "MACD_Signal"]].tail())

def load_raw_data(ticker):
    raw_path = Path(__file__).resolve().parents[1] / "data" / "raw" / f"{ticker}.csv"
    df = pd.read_csv(raw_path, parse_dates=["Date"], index_col="Date")
    return df

if __name__ == "__main__":
    run()
