🧠 TRADEBOT7 DAILY UPDATE – Execution Protocol
Check position meta (updated) before running flag and stop of data is not update todate between different data sorces (local and CS csv)
This daily process ensures positions are actively managed to outperform the S&P while aligning with your risk, allocation, and tactical goals.

⚠️ TRUSTED DATA ENFORCEMENT:
Only use indicators (RSI, MACD, SMA) if sourced from a verified provider (e.g. Yahoo Finance, Finviz).
If indicators are unavailable or outdated, output must include:
- ⚠️ `data_status: simulated` or `📦 Estimated`
- And avoid any signal-based recommendations.

All final indicator blocks must include `"source":` and `"fetched_at":` fields.

⚠️ IMPORTANT:
🛑 Only use indicator data (like RSI, MACD, SMA) if pulled from a trusted live source (e.g., Yahoo, Finviz).
⚠️ If no trusted data is available, I must clearly flag it as “⚠️ Simulated” or “📦 Estimated.”
⸻

🔁 1. Review and Update All Positions
	•	Inspect each position in positions.json
	•	Update or confirm:
	•	"action" — e.g. "HOLD", "TRIM", "REVIEW"
	•	"stop_loss" or "trailing_stop" based on current support/resistance
	•	"narrative" — 1–2 sentence rationale grounded in price action and macro context
	•	"consider_trim": true if gain > 20% or nearing overbought/resistance

⸻

📈 2. Apply Market Context
	•	Factor in:
	•	Current sector strength/rotation (e.g. tech, energy, healthcare)
	•	Relevant macro headlines (e.g. interest rate shifts, jobs reports)
	•	Earnings reports or major events tied to positions
	•	Adjust actions and risk based on volatility, sentiment, and price behavior

⸻

🛡️ 3. Align Risk (Stops) and Opportunity (Targets)
	•	Every position should have a defined risk guardrail:
	•	Stop-loss or trailing stop
	•	Conservative setups: 3–5% below support
	•	Volatile/spec setups: wider 10–15% stop
	•	Identify potential take-profit zones where gains should be locked in

⸻

💸 4. Profit-Taking / Reallocation
	•	Tag "consider_trim": true for:
	•	Positions up > 20%
	•	Stocks that are overextended or approaching prior highs
	•	Adjust "narrative" to include rationale for trimming or watching

⸻

🧾 5. Update positions.json
	•	Make all edits directly in the file:
	•	Updated prices, market values
	•	Actions and narratives
	•	Stop or trailing stop values
	•	"meta.last_updated" and "meta.cash_available" must be current

⸻

🧮 6. Compile and Save Report
	•	Generate a markdown file named:
YYYY-MM-DD_DailyUpdate.md

It must include:
	•	✅ Overall portfolio performance (value, cost, gain/loss %)
	•	✅ Top 5 strengths (biggest winners)
	•	✅ Top 3–5 weaknesses/risks (biggest losers or review tags)
	•	✅ Tactical opportunities and reasoning
	•	✅ 5 specific strategic recommendations
	•	✅ Capital deployment plan based on actual "cash_available"
	•	✅ Next steps checklist (actionable tomorrow)
	•	✅ S&P 500 change pulled from CNBC or equivalent — no simulation. If data is unavailable, skip and tag report as ⚠️ Estimated.

⸻
