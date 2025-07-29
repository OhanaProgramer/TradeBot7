# test/test_util.py
import os
import pandas as pd

# Define base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")
AAPL_PATH = os.path.join(RAW_DIR, "AAPL.csv")

def load_price_data(file_path=AAPL_PATH):
    """Load raw AAPL price data and return a pandas DataFrame."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    
    df = pd.read_csv(file_path)
    
    # Validate expected columns
    required_cols = {"Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")
    
    # Parse Date column
    df["Date"] = pd.to_datetime(df["Date"])
    
    return df

if __name__ == "__main__":
    df = load_price_data()
    print(f"✅ Loaded AAPL data from {AAPL_PATH} with shape {df.shape}")
    print(df.head(5))