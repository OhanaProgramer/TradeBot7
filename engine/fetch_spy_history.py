# fetch_spy_history.py
import yfinance as yf
import pandas as pd
from datetime import datetime

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "raw", "SPY_history.csv")

# Customize your date range
START_DATE = "2021-01-01"
END_DATE = datetime.today().strftime('%Y-%m-%d')

# Fetch SPY data from Yahoo Finance
spy = yf.Ticker("SPY")
hist = spy.history(start=START_DATE, end=END_DATE)

# Format and export
hist = hist[["Close"]].reset_index()
hist.columns = ["date", "close"]
hist["date"] = hist["date"].dt.date  # simplify to YYYY-MM-DD

# Save to CSV
hist.to_csv(OUTPUT_PATH, index=False)

print("✅ SPY_history.csv saved.")