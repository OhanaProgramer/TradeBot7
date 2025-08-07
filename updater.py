import requests
import json
from datetime import datetime
import os

API_KEY = '1aca3de48e43413fbcd1a217d771d70d'  # 🔑 Replace with your TwelveData API key

symbols = ['AAPL', 'NVDA', 'PLNT']  # 🔁 Add your tickers
print("🔍 Starting indicator fetch for:", symbols)
def fetch_rsi(symbol):
    print(f"Fetching RSI for {symbol}")
    url = f'https://api.twelvedata.com/rsi?symbol={symbol}&interval=1day&apikey={API_KEY}'
    response = requests.get(url).json()
    return float(response['values'][0]['rsi']) if 'values' in response else None

def fetch_macd(symbol):
    print(f"Fetching MACD for {symbol}")
    url = f'https://api.twelvedata.com/macd?symbol={symbol}&interval=1day&apikey={API_KEY}'
    response = requests.get(url).json()
    return response['values'][0] if 'values' in response else None

def fetch_sma(symbol, period):
    print(f"Fetching SMA for {symbol} with period {period}")
    url = f'https://api.twelvedata.com/sma?symbol={symbol}&interval=1day&time_period={period}&apikey={API_KEY}'
    response = requests.get(url).json()
    return float(response['values'][0]['sma']) if 'values' in response else None

base_dir = os.path.dirname(__file__)
positions_path = os.path.join(base_dir, 'data', 'positions.json')
with open(positions_path, 'r+') as f:
    data = json.load(f)
    for pos in data.get('positions', []):
        if 'symbol' not in pos:
            print(f"⚠️ Skipping entry without 'symbol': {pos}")
            continue
        symbol = pos['symbol']
        try:
            pos['indicators'] = {
                "RSI": fetch_rsi(symbol),
                "MACD": fetch_macd(symbol),
                "SMA_20": fetch_sma(symbol, 20),
                "SMA_50": fetch_sma(symbol, 50),
                "SMA_200": fetch_sma(symbol, 200),
                "source": "TwelveData",
                "fetched_at": datetime.now().isoformat()
            }
            print(f"✅ Indicators fetched for {symbol}")
        except Exception as e:
            print(f"❌ Failed to fetch indicators for {symbol}: {e}")
            pos['indicators'] = {"note": "Fetch failed", "error": str(e)}

    if "meta" not in data:
        data["meta"] = {}
    data["meta"]["last_updated_indicators"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    f.seek(0)
    json.dump(data, f, indent=2)
    f.truncate()
    print("✅ Finished updating positions.json")
