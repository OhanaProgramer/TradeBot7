
from datetime import datetime
import pandas as pd
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
import numpy as np

# === STRATEGY CONTEXT ===
# The current simulation uses:
# - RSI_14 for buy/sell signal thresholds
# - SMA_50 and SMA_200 for trend confirmation
# - Simulation assumes all-in on signal, full exit on sell
# - Starting cash: $10,000
# - No MACD or volatility indicators yet
# - Target return is based on AAPL total return over date range
#
# NOTE: Preserve this context when expanding strategies

BASE_DIR = Path(__file__).resolve().parents[1]
SIGNALS_DIR = BASE_DIR / "data" / "signals"
PORTFOLIO_PATH = BASE_DIR / "data" / "static" / "portfolio.json"


console = Console()

# Optimization parameters
RSI_BUY_RANGE = range(20, 36, 2)
RSI_SELL_RANGE = range(60, 81, 2)

def load_portfolio():
    with open(PORTFOLIO_PATH, "r") as f:
        return json.load(f)["position_list"]

def load_signals(ticker):
    path = SIGNALS_DIR / f"{ticker}_signals.csv"
    df = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
    df.name = ticker
    return df

def simulate_trades(df, strategy):
    position_open = False
    entry_price = 0
    trades = []
    portfolio_value = 0
    cash = 10000  # starting capital
    equity_curve = []

    for date, row in df.iterrows():
        try:
            rsi = row["RSI_14"]
            price = row["Adj Close"]

            bullish = rsi < strategy.get("rsi_buy", 30)
            bearish = rsi > strategy.get("rsi_sell", 70)

            if not position_open and bullish:
                position_open = True
                entry_price = price
                qty = cash / entry_price
                cash = 0
                trades.append((date, "BUY", entry_price))

            elif position_open and bearish:
                position_open = False
                exit_price = price
                cash = qty * exit_price
                portfolio_value = cash
                trades.append((date, "SELL", exit_price))

            # Track equity value
            current_value = cash if not position_open else qty * price
            equity_curve.append(current_value)

        except Exception:
            continue  # skip any problematic row

    if position_open:
        final_price = df.iloc[-1]["Adj Close"]
        cash = qty * final_price
        portfolio_value = cash
        equity_curve.append(portfolio_value)

    # Compute daily returns
    daily_returns = pd.Series(equity_curve).pct_change().dropna()
    if not daily_returns.empty:
        sharpe_ratio = (daily_returns.mean() - 0.00015) / daily_returns.std()
    else:
        sharpe_ratio = 0

    return trades, portfolio_value, sharpe_ratio

def run_optimization(target_return=None):
    portfolio = load_portfolio()
    for pos in portfolio:
        ticker = pos["ticker"]
        df = load_signals(ticker)

        spy_df = pd.read_csv(BASE_DIR / "data" / "raw" / "SPY_history.csv", parse_dates=["Date"], index_col="Date")
        spy_df.columns = spy_df.columns.str.strip()
        spy_df = spy_df.loc[df.index.min():df.index.max()]
        spy_return = (spy_df["Close"].iloc[-1] - spy_df["Close"].iloc[0]) / spy_df["Close"].iloc[0] * 100
        console.print(f"[bold yellow]Evaluating position: {ticker}[/bold yellow]")
        console.print(f"\n[bold cyan]RSI Optimization Compared to SPY Benchmark for {ticker}[/bold cyan]")
        console.print(f"[green]SPY Return over same period: {spy_return:.2f}%[/green]")
        # Use AAPL return over same period as the new target return
        df_return = (df["Adj Close"].iloc[-1] - df["Adj Close"].iloc[0]) / df["Adj Close"].iloc[0] * 100
        console.print(f"[green]{ticker} Return over same period: {df_return:.2f}%[/green]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Buy <", justify="right")
        table.add_column("Sell >", justify="right")
        table.add_column("Return (%)", justify="right")
        table.add_column("Δ from AAPL Target", justify="right")
        table.add_column("Sharpe", justify="right")
        table.add_column("Alpha", justify="right")

        results = []
        for rsi_buy in RSI_BUY_RANGE:
            for rsi_sell in RSI_SELL_RANGE:
                strategy = {
                    "rsi_buy": rsi_buy,
                    "rsi_sell": rsi_sell
                }
                try:
                    trades, final_value, sharpe_ratio = simulate_trades(df, strategy)
                    pct_return = (final_value - 10000) / 10000 * 100
                    delta = abs(pct_return - df_return)
                    alpha = pct_return - df_return
                    results.append({
                        "rsi_buy": rsi_buy,
                        "rsi_sell": rsi_sell,
                        "pct_return": pct_return,
                        "delta": delta,
                        "sharpe": sharpe_ratio,
                        "alpha": alpha
                    })
                except Exception as e:
                    console.print(f"[red]Error with strategy {strategy}: {e}[/red]")

        # Sort results by Sharpe Ratio descending
        results.sort(key=lambda x: x["sharpe"], reverse=True)
        results = results[:10]

        for result in results:
            table.add_row(
                str(result["rsi_buy"]),
                str(result["rsi_sell"]),
                f"{result['pct_return']:.2f}%",
                f"{result['delta']:.2f}%",
                f"{result['sharpe']:.2f}",
                f"{result['alpha']:.2f}%"
            )

        console.print(table)

        total_trades = sum(len(simulate_trades(df, {"rsi_buy": r["rsi_buy"], "rsi_sell": r["rsi_sell"]})[0]) for r in results)
        avg_trades = total_trades / len(results) if results else 0
        console.print(f"\n[bold blue]Average number of trades (top 10 strategies): {avg_trades:.2f}[/bold blue]")

if __name__ == "__main__":
    run_optimization()