import pandas as pd
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table

BASE_DIR = Path(__file__).resolve().parents[1]
SIGNALS_DIR = BASE_DIR / "data" / "signals"
PORTFOLIO_PATH = BASE_DIR / "data" / "static" / "portfolio.json"

console = Console()

def load_portfolio():
    with open(PORTFOLIO_PATH, "r") as f:
        return json.load(f)["position_list"]

def load_signals(ticker):
    path = SIGNALS_DIR / f"{ticker}_signals.csv"
    return pd.read_csv(path, parse_dates=["Date"], index_col="Date")

def simulate_trades(df, strategy):
    position_open = False
    entry_price = 0
    trades = []
    portfolio_value = 0
    cash = 10000  # starting capital

    for date, row in df.iterrows():
        # Simple rule: buy when all bullish, sell when all bearish
        bullish = row["RSI_14"] < strategy.get("rsi_buy", 30) and row["SMA_50"] > row["SMA_200"]
        bearish = row["RSI_14"] > strategy.get("rsi_sell", 70) and row["SMA_50"] < row["SMA_200"]

        if not position_open and bullish:
            position_open = True
            entry_price = row["Adj Close"]
            qty = cash / entry_price
            cash = 0
            trades.append((date, "BUY", entry_price))
        
        elif position_open and bearish:
            position_open = False
            exit_price = row["Adj Close"]
            cash = qty * exit_price
            portfolio_value = cash
            trades.append((date, "SELL", exit_price))

    if position_open:
        # close last open trade
        cash = qty * df.iloc[-1]["Adj Close"]
        portfolio_value = cash

    return trades, portfolio_value

def run():
    portfolio = load_portfolio()
    for pos in portfolio:
        ticker = pos["ticker"]
        df = load_signals(ticker)
        trades, final_value = simulate_trades(df, pos.get("strategy", {}))

        console.print(f"\n[bold cyan]Backtest Results for {ticker}[/bold cyan]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Date", style="dim")
        table.add_column("Action")
        table.add_column("Price", justify="right")

        for date, action, price in trades:
            table.add_row(str(date.date()), action, f"{price:.2f}")

        console.print(table)
        console.print(f"[bold green]Final Portfolio Value:[/bold green] ${final_value:.2f}")

if __name__ == "__main__":
    run()