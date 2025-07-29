from flask import Flask, render_template, jsonify
import yfinance as yf
import json

app = Flask(__name__)

@app.route('/')
def index():
    with open('data/strategy.json') as f:
        strategy = json.load(f)
    with open('data/dailyChecklist.json') as f:
        checklist = json.load(f)

    # Calculate dynamic trailing stops before rendering table
    for s in strategy:
        if (
            s.get('stop_type') == 'trailing'
            and s.get('stop_loss') is not None
            and s.get('price') is not None
        ):
            try:
                existing_stop = float(s['stop_loss'])
                price = float(s['price'])
                new_stop = max(existing_stop, price * (1 - 0.05))
                s['stop_loss'] = round(new_stop, 2)
            except Exception:
                pass

    # Create a mapping from ticker → action_needed
    actions = {item['ticker']: item['action_needed'] for item in checklist}

    # Merge action_needed into strategy data
    for s in strategy:
        s['action_needed'] = actions.get(s['ticker'], 'Pending')

    return render_template('index.html', data=strategy)

import yfinance as yf
from flask import jsonify

@app.route('/api/live/<ticker>')
def live_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")['Close'].iloc[-1]
        return jsonify({"ticker": ticker, "live_price": round(price, 2)})
    except Exception as e:
        return jsonify({"ticker": ticker, "error": str(e), "live_price": None})

@app.route('/api/strategy')
def get_strategy():
    with open('data/strategy.json') as f:
        strategy = json.load(f)
    return jsonify(strategy)

if __name__ == '__main__':
    app.run(debug=True)