# 🧠 TRADEBOT7 DAILY UPDATE – Execution Protocol (2025-08-06)

This daily process ensures positions are actively managed to outperform the S&P while aligning with your risk, allocation, and tactical goals.

⚠️ **IMPORTANT**  
If `positions.json` is outdated or does not contain current close data, you must issue a clear warning and **NOT simulate values**.  
**No actions, recommendations, or markdown reports should be generated until data is fully updated.**

---

## 🔁 1. Review and Update All Positions
- Inspect each position in `positions.json`
- Update or confirm:
  - `"action"` — e.g. `"HOLD"`, `"TRIM"`, `"REVIEW"`
  - `"stop_loss"` or `"trailing_stop"` based on current support/resistance
  - `"narrative"` — 1–2 sentence rationale grounded in price action and macro context
  - `"consider_trim": true` if gain > 20% or nearing overbought/resistance

---

## 📈 2. Apply Market Context
- Factor in:
  - Current **sector strength/rotation** (e.g. tech, energy, healthcare)
  - Relevant **macro headlines** (e.g. interest rate shifts, jobs reports)
  - **Earnings reports** or major events tied to positions
- Adjust actions and risk based on volatility, sentiment, and price behavior

---

## 🛡️ 3. Align Risk (Stops) and Opportunity (Targets)
- Every position should have a defined risk guardrail:
  - Stop-loss or trailing stop
  - Conservative setups: 3–5% below support
  - Volatile/spec setups: wider 10–15% stop
- Identify potential take-profit zones where gains should be locked in

---

## 💸 4. Profit-Taking / Reallocation
- Tag `"consider_trim": true` for:
  - Positions up > 20%
  - Stocks that are overextended or approaching prior highs
- Adjust `"narrative"` to include rationale for trimming or watching

---

## 🧾 5. Update `positions.json`
- Make all edits directly in the file:
  - Updated prices, market values
  - Actions and narratives
  - Stop or trailing stop values
  - `"meta.last_updated"` and `"meta.cash_available"` must be current

---


## 🧮 6. Compile and Save Report
- Generate a markdown file named:  
  `<datae>DailyUpdate.md`

It must include:
- ✅ Overall portfolio performance (value, cost, gain/loss %)
- ✅ Top 5 strengths (biggest winners)
- ✅ Top 3–5 weaknesses/risks (biggest losers or review tags)
- ✅ Tactical opportunities and reasoning
- ✅ 5 specific strategic recommendations
- ✅ Capital deployment plan based on actual `"cash_available"` ($4,366.23)
- ✅ Next steps checklist (actionable tomorrow)
- ✅ S&P 500 change pulled from CNBC or equivalent (no simulation)

---

## ⏰ Trade Alerts and Buy Prep (2025-08-06)

### 🔔 Alerts to Set
| Symbol | Type         | Trigger Level | Reason |
|--------|--------------|---------------|--------|
| JNJ    | Upper Alert  | $170.00       | Watch for breakout confirmation above resistance |
| HD     | Upper Alert  | $375.00       | Confirm reversal strength after recent rally |
| META   | RSI Alert    | RSI > 70      | Potential trim trigger based on momentum |
| NVDA   | Price Alert  | $1300.00      | Take partial profits per plan |
| AMZN   | Price Alert  | $190.00       | Watch for resistance zone entry |
| BAC    | Price Alert  | $41.00        | Monitor for potential trim opportunity |
| GOOG   | Price Alert  | $185.00       | Near prior highs; potential profit-taking zone |

### 🛒 Buy Order Prep
| Symbol | Entry Type   | Target Price | Order Type | Notes |
|--------|--------------|--------------|------------|-------|
| PLNT   | Support Dip  | $107.00      | Limit      | Watch for bounce near support zone |
| RPI    | Speculative  | $4.50        | GTC Limit  | Only if volume confirms setup |
| VGT    | Support Dip  | $682.00      | Limit      | Wait for bounce near support |
| MSFT   | Breakout     | $515.00      | Alert      | Wait for confirmation above resistance |
| GOOGL  | Add-on Dip   | $175.00      | Alert      | Entry only with cash and trend confirmation |
| AMZN   | Add-on Dip   | $182.00      | Alert      | Confirm strength before re-entry |
