
from datetime import datetime
import pandas as pd
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
import numpy as np
import time
from rich.progress import Progress

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

# Additional indicator toggles for grid search
USE_MACD = [False, True]
USE_BB = [False, True]
USE_ATR = [False, True]

def load_portfolio():
    with open(PORTFOLIO_PATH, "r") as f:
        return json.load(f)["position_list"]

def load_signals(ticker):
    path = SIGNALS_DIR / f"{ticker}_signals.csv"
    df = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
    df.name = ticker
    return df

#
# === simulate_trades ===
# This function runs a backtest for a single strategy defined by RSI buy/sell thresholds.
# - Buys when RSI falls below the buy threshold and no position is open.
# - Sells when RSI rises above the sell threshold and a position is open.
# - Tracks cash, position, and equity curve to compute final portfolio value and Sharpe Ratio.
#
def simulate_trades(df, strategy):
    position_open = False
    entry_price = 0
    trades = []
    portfolio_value = 0
    cash = 10000  # starting capital
    equity_curve = []

    for date, row in df.iterrows():
        try:
            # Retrieve RSI and current price for this day
            rsi = row["RSI_14"]
            price = row["Adj Close"]

            # Retrieve Bollinger Bands and ATR if available
            bb_upper = row.get("BB_Upper", None)
            bb_lower = row.get("BB_Lower", None)
            atr = row.get("ATR_14", None)

            # --- MACD extraction and diff ---
            macd = row.get("MACD", None)
            signal = row.get("Signal", None)
            macd_diff = None
            if macd is not None and signal is not None:
                macd_diff = macd - signal

            # RSI conditions as before
            rsi_buy_cond = rsi < strategy.get("rsi_buy", 30)
            rsi_sell_cond = rsi > strategy.get("rsi_sell", 70)

            # --- Bollinger Band conditions ---
            bb_buy_cond = True
            bb_sell_cond = True
            if bb_lower is not None and not np.isnan(bb_lower):
                bb_buy_cond = price <= bb_lower  # buy when price near/below lower band
            if bb_upper is not None and not np.isnan(bb_upper):
                bb_sell_cond = price >= bb_upper  # sell when price near/above upper band

            # --- ATR volatility filter ---
            atr_cond = True
            if atr is not None and not np.isnan(atr):
                atr_cond = atr > 0  # only trade if ATR is positive (avoid flat data)

            # --- MACD crossover detection ---
            # Tracks whether MACD crosses above/below Signal compared to previous day
            macd_buy_cond = True
            macd_sell_cond = True

            if macd_diff is not None:
                prev_macd_diff = None

                # Access previous row's MACD-Signal difference if available
                try:
                    prev_macd = df.shift(1).loc[date]["MACD"]
                    prev_signal = df.shift(1).loc[date]["Signal"]
                    if not np.isnan(prev_macd) and not np.isnan(prev_signal):
                        prev_macd_diff = prev_macd - prev_signal
                except Exception:
                    prev_macd_diff = None

                # Crossover: negative→positive for buy, positive→negative for sell
                if prev_macd_diff is not None:
                    macd_buy_cond = prev_macd_diff < 0 and macd_diff > 0
                    macd_sell_cond = prev_macd_diff > 0 and macd_diff < 0

            bullish = rsi_buy_cond and macd_buy_cond and bb_buy_cond and atr_cond
            bearish = rsi_sell_cond and macd_sell_cond and bb_sell_cond and atr_cond

            # Buy condition: enter the market with full cash
            if not position_open and bullish:
                position_open = True
                entry_price = price
                qty = cash / entry_price
                cash = 0
                trades.append((date, "BUY", entry_price))

            # Sell condition: exit market and realize gains/losses
            elif position_open and bearish:
                position_open = False
                exit_price = price
                cash = qty * exit_price
                portfolio_value = cash
                trades.append((date, "SELL", exit_price))

            # Track the portfolio value at the end of the day
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

#
# === run_optimization ===
# This function:
# 1. Loads each position from the portfolio.
# 2. Loads historical signals for that ticker.
# 3. Computes the benchmark (SPY) return for the same period.
# 4. Iterates over RSI buy/sell parameter ranges, running simulate_trades for each.
# 5. Collects results including % Return, Delta from target (AAPL buy/hold), Sharpe, and Alpha.
# 6. Sorts the top 10 strategies by Sharpe Ratio and prints them in a table.
#
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

        # === Progress Bar Setup ===
        total_iters = len(USE_MACD) * len(USE_BB) * len(USE_ATR) * len(RSI_BUY_RANGE) * len(RSI_SELL_RANGE)
        current_iter = 0
        start_time = time.time()
        progress = Progress()
        task = progress.add_task(f"[cyan]Optimizing {ticker}...", total=total_iters)

        with progress:
            for use_macd in USE_MACD:
                for use_bb in USE_BB:
                    for use_atr in USE_ATR:
                        for rsi_buy in RSI_BUY_RANGE:
                            for rsi_sell in RSI_SELL_RANGE:
                                current_iter += 1
                                elapsed = time.time() - start_time
                                progress.update(
                                    task,
                                    advance=1,
                                    description=f"[green]{ticker} {current_iter}/{total_iters} | {elapsed:.1f}s elapsed[/green]"
                                )

                                strategy = {
                                    "rsi_buy": rsi_buy,
                                    "rsi_sell": rsi_sell,
                                    "use_macd": use_macd,
                                    "use_bb": use_bb,
                                    "use_atr": use_atr
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
        results = results[:3]

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

        # Compute and display the average number of trades executed for the top 3 strategies.
        total_trades = sum(len(simulate_trades(df, {"rsi_buy": r["rsi_buy"], "rsi_sell": r["rsi_sell"]})[0]) for r in results)
        avg_trades = total_trades / len(results) if results else 0
        console.print(f"\n[bold blue]Average number of trades (top 3 strategies): {avg_trades:.2f}[/bold blue]")

if __name__ == "__main__":
    run_optimization()