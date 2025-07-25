import yfinance as yf
import os
from datetime import datetime, timedelta
import pandas as pd
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
PORTFOLIO_PATH = os.path.join(BASE_DIR, "data", "static", "portfolio.json")

with open(PORTFOLIO_PATH, "r") as f:
    portfolio_data = json.load(f)

TICKERS = [pos["name"] for pos in portfolio_data.get("position_list", [])]
os.makedirs(OUTPUT_DIR, exist_ok=True)

end = datetime.today()
start = end - timedelta(days=5 * 365)

success_count = 0
for ticker in TICKERS:
    try:
        df = yf.download(ticker, start=start.strftime('%Y-%m-%d'), auto_adjust=False)
        df = df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]]
        df.dropna(inplace=True)
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.reset_index().rename(columns={"date": "Date"})  # ensure 'Date' is a column
        df.columns = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
        ticker_obj = yf.Ticker(ticker)

        # Save dividend history
        divs = ticker_obj.dividends
        if not divs.empty:
            divs.index.name = "Date"
            divs.to_csv(f"{OUTPUT_DIR}/{ticker}_dividends.csv", index_label="Date")

        # Save split history
        splits = ticker_obj.splits
        if not splits.empty:
            splits.index.name = "Date"
            splits.to_csv(f"{OUTPUT_DIR}/{ticker}_splits.csv", index_label="Date")

        if not df.empty:
            file_path = os.path.join(OUTPUT_DIR, f"{ticker}.csv")
            df.to_csv(file_path, index=False)

            # Clean up metadata line artifacts (if any)
            with open(file_path, "r") as f:
                lines = f.readlines()
            if len(lines) > 3 and "Ticker" in lines[1] and "Date" in lines[2]:
                with open(file_path, "w") as f:
                    f.writelines([lines[0]] + lines[3:])

            print(f"[✓] Saved {ticker} to {file_path}")
            success_count += 1
        else:
            print(f"[!] No data for {ticker}")
    except Exception as e:
        print(f"[X] {ticker}: {e}")

print(f"\n[✓] Successfully fetched data for {success_count} of {len(TICKERS)} tickers.")