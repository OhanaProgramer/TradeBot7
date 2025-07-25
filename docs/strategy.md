<file name=strategy_guidelines.md path=/Users/jacquewilson/Documents/Projects/TradeBot7/docs># 🧠 TradeBot7 Strategy Considerations

## 1️⃣ Stock Characteristics and Strategy Impact

| **Factor**        | **Example**                 | **Impact on Strategy**                             |
|-------------------|-----------------------------|---------------------------------------------------|
| **Volatility**    | NIO is more volatile than AAPL | Use RSI for quick extremes, avoid slow SMA signals |
| **Trend Behavior**| AAPL respects long-term trends| SMA 50/200 crossovers work well                   |
| **Liquidity**     | Large-cap vs small-cap      | MACD is more reliable with high liquidity         |
| **Dividend/Events**| High dividend stocks        | Adjust RSI thresholds around ex-dividend dates    |

---

## 2️⃣ Risk Tolerance

- **High risk tolerance:** Use RSI and short-term signals for swing trades.  
- **Low risk tolerance:** Favor SMA/long-term moving averages; avoid false signals.

---

## 3️⃣ Backtesting & Observation

1. Fetch 5 years of historical data (via `fetch.py`).  
2. Backtest each indicator’s performance per ticker.  
3. Adjust thresholds dynamically if performance is poor.  

---

## 4️⃣ Indicator Guidelines (Default Thresholds)

| **Indicator** | **Bullish Signal**                       | **Bearish Signal**                     |
|---------------|------------------------------------------|---------------------------------------|
| **RSI**       | < 30 (Oversold, buy consideration)       | > 70 (Overbought, sell consideration) |
| **MACD**      | MACD crosses above Signal line           | MACD crosses below Signal line        |
| **SMA**       | SMA_50 > SMA_200 (Golden Cross)          | SMA_50 < SMA_200 (Death Cross)        |

---

## 5️⃣ Applying Strategies Per Ticker

1. Start with default thresholds (RSI 30/70, SMA 50/200, MACD crossover).  
2. Adjust per ticker based on observed behavior and backtesting results.  
3. Store these parameters per ticker in `portfolio.json` under the `strategy` section.  
4. Let `evaluate.py` dynamically use these settings for signal interpretation.

---

## ✅ Example Strategy JSON

```json