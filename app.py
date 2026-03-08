"""
Flask Web Server — AI Financial Advisor ka web frontend serve karta hai.
"""
import csv
import json
import os
import flask
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = flask.Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24).hex())

USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.json')


def _load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}


def _save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)


def _get_logged_in_user():
    """Returns the logged in user's profile data or None."""
    username = flask.session.get('username')
    if not username:
        return None
    users = _load_users()
    user_entry = users.get(username)
    if not user_entry or not user_entry.get('profile'):
        return None
    return user_entry['profile']

from advisor import get_latest_user_profile, get_market_predictions, generate_ai_advice
from risk_engine import get_risk_summary
from portfolio_generator import generate_portfolio
from report_generator import generate_report_file
from cloud_fetcher import fetch_and_save as fetch_live_data
import threading
import pandas as pd
from datetime import datetime

_fetch_lock = threading.Lock()
_last_fetch_time = None


@app.route('/')
def index():
    return flask.render_template('index.html')


# ---------- AUTH ENDPOINTS ----------

@app.route('/api/register', methods=['POST'])
def api_register():
    data = flask.request.get_json()
    username = str(data.get('username', '')).strip().lower()
    password = str(data.get('password', ''))
    phone = str(data.get('phone', '')).strip()

    if not username or not password:
        return flask.jsonify({"status": "error", "message": "Username and password are required."})
    if len(username) < 3:
        return flask.jsonify({"status": "error", "message": "Username must be at least 3 characters."})
    if len(password) < 4:
        return flask.jsonify({"status": "error", "message": "Password must be at least 4 characters."})

    users = _load_users()
    if username in users:
        return flask.jsonify({"status": "error", "message": "Username already exists. Please login."})

    users[username] = {
        "password_hash": generate_password_hash(password),
        "phone": phone,
        "profile": None
    }
    _save_users(users)

    flask.session['username'] = username
    return flask.jsonify({"status": "ok", "message": "Account created!", "username": username})


@app.route('/api/login', methods=['POST'])
def api_login():
    data = flask.request.get_json()
    username = str(data.get('username', '')).strip().lower()
    password = str(data.get('password', ''))

    if not username or not password:
        return flask.jsonify({"status": "error", "message": "Username and password are required."})

    users = _load_users()
    user_entry = users.get(username)
    if not user_entry or not check_password_hash(user_entry['password_hash'], password):
        return flask.jsonify({"status": "error", "message": "Invalid username or password."})

    flask.session['username'] = username
    has_profile = user_entry.get('profile') is not None
    return flask.jsonify({"status": "ok", "message": "Login successful!", "username": username, "has_profile": has_profile})


@app.route('/api/logout', methods=['POST'])
def api_logout():
    flask.session.pop('username', None)
    return flask.jsonify({"status": "ok", "message": "Logged out."})


@app.route('/api/me', methods=['GET'])
def api_me():
    username = flask.session.get('username')
    if not username:
        return flask.jsonify({"status": "error", "logged_in": False})
    users = _load_users()
    user_entry = users.get(username, {})
    return flask.jsonify({
        "status": "ok",
        "logged_in": True,
        "username": username,
        "has_profile": user_entry.get('profile') is not None
    })


# ---------- PROFILE ENDPOINTS ----------

@app.route('/api/profile', methods=['GET'])
def api_get_profile():
    user = _get_logged_in_user()
    if user:
        return flask.jsonify({"status": "ok", "data": user})
    if not flask.session.get('username'):
        return flask.jsonify({"status": "error", "message": "Please login first."})
    return flask.jsonify({"status": "error", "message": "No profile found. Create one first."})


@app.route('/api/profile', methods=['POST'])
def api_save_profile():
    username = flask.session.get('username')
    if not username:
        return flask.jsonify({"status": "error", "message": "Please login first."})

    data = flask.request.get_json()
    name = str(data.get('name', '')).strip()
    age = data.get('age')
    income = data.get('income')
    savings = data.get('savings')
    expenses = data.get('expenses')

    if not name or age is None or income is None or savings is None or expenses is None:
        return flask.jsonify({"status": "error", "message": "All fields are required."})

    try:
        age = int(age)
        income = float(income)
        savings = float(savings)
        expenses = float(expenses)
    except (ValueError, TypeError):
        return flask.jsonify({"status": "error", "message": "Invalid numeric values."})

    user_data = {"Name": name, "Age": age, "Income": income, "Savings": savings, "Expenses": expenses}

    # Save to user's account
    users = _load_users()
    if username in users:
        users[username]['profile'] = user_data
        _save_users(users)

    # Also save to CSV for compatibility with advisor.py
    file_path = 'user_profile.csv'
    file_exists = os.path.isfile(file_path)
    with open(file_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=user_data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(user_data)

    return flask.jsonify({"status": "ok", "message": "Profile saved!", "data": user_data})


@app.route('/api/fetch-data', methods=['POST'])
def api_fetch_data():
    """Fetch fresh market data from Yahoo Finance."""
    global _last_fetch_time
    if not _fetch_lock.acquire(blocking=False):
        return flask.jsonify({"status": "ok", "message": "Fetch already in progress...", "fetching": True})
    try:
        fetch_live_data()
        _last_fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return flask.jsonify({"status": "ok", "message": "Fresh data fetched!", "last_updated": _last_fetch_time})
    except Exception as e:
        return flask.jsonify({"status": "error", "message": f"Fetch failed: {str(e)}"})
    finally:
        _fetch_lock.release()


@app.route('/api/predictions', methods=['GET'])
def api_predictions():
    # Get last updated time from CSV
    last_updated = None
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'market_tracker.csv')
    if os.path.exists(csv_path):
        try:
            df_time = pd.read_csv(csv_path)
            if 'Time' in df_time.columns and len(df_time) > 0:
                last_updated = str(df_time['Time'].iloc[-1])
        except Exception:
            pass

    stocks = get_market_predictions()
    if stocks:
        buy = sum(1 for s in stocks if s['action'] == 'BUY')
        sell = sum(1 for s in stocks if s['action'] == 'SELL')
        hold = sum(1 for s in stocks if s['action'] == 'HOLD')
        return flask.jsonify({"status": "ok", "data": stocks,
            "summary": {"buy": buy, "sell": sell, "hold": hold, "total": len(stocks)},
            "last_updated": last_updated})
    return flask.jsonify({"status": "error", "message": "No market data. Fetch data first."})


@app.route('/api/chart-data', methods=['GET'])
def api_chart_data():
    """Returns historical prices + ML predicted future prices for a specific stock."""
    symbol = flask.request.args.get('symbol', '')
    if not symbol:
        return flask.jsonify({"status": "error", "message": "Symbol parameter required."})

    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'market_tracker.csv')
    if not os.path.exists(csv_path):
        return flask.jsonify({"status": "error", "message": "No market data found."})

    try:
        df = pd.read_csv(csv_path)
        df.columns = ['Time', 'Symbol', 'Price']
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df = df.dropna()
    except Exception:
        return flask.jsonify({"status": "error", "message": "Error reading market data."})

    stock_df = df[df['Symbol'] == symbol].copy()
    if len(stock_df) == 0:
        return flask.jsonify({"status": "error", "message": f"No data for {symbol}."})

    times = stock_df['Time'].tolist()
    prices = stock_df['Price'].tolist()

    import numpy as np
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.linear_model import Ridge, LinearRegression as LR
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

    price_arr = np.array(prices)
    n = len(price_arr)
    X = np.arange(n).reshape(-1, 1)

    # --- 1. Polynomial Trend (degree 3) for historical data ---
    degree = min(3, max(1, n // 5))
    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)
    trend_model = Ridge(alpha=1.0)
    trend_model.fit(X_poly, price_arr)
    trend_line = trend_model.predict(X_poly).tolist()
    trend_line = [round(p, 2) for p in trend_line]

    # --- 2. Smoothed actual prices (EMA) ---
    ema_span = max(1, min(5, n // 3))
    smoothed = pd.Series(prices).ewm(span=ema_span, adjust=False).mean().tolist()
    smoothed = [round(p, 2) for p in smoothed]

    # --- 3. Future predictions — FOUR models ---
    future_steps = 5

    # Model A: Polynomial extrapolation (overall trend direction)
    X_future_abs = np.arange(n, n + future_steps).reshape(-1, 1)
    X_future_poly = poly.transform(X_future_abs)
    trend_future = trend_model.predict(X_future_poly).tolist()
    trend_future = [round(p, 2) for p in trend_future]

    # Model B: Weighted regression on recent data (short-term momentum)
    recent_n = min(10, n)
    recent_prices = price_arr[-recent_n:]
    X_recent = np.arange(recent_n).reshape(-1, 1)
    weights = np.exp(np.linspace(0, 2, recent_n))
    future_model = LR()
    future_model.fit(X_recent, recent_prices, sample_weight=weights)
    X_future_rel = np.arange(recent_n, recent_n + future_steps).reshape(-1, 1)
    momentum_future = future_model.predict(X_future_rel).tolist()
    momentum_future = [round(p, 2) for p in momentum_future]

    # Model C: Random Forest Regressor (lag features)
    def _build_lag_features(arr, lag=3):
        Xf, yf = [], []
        for i in range(lag, len(arr)):
            Xf.append(arr[i-lag:i])
            yf.append(arr[i])
        return np.array(Xf), np.array(yf)

    lag = min(3, n - 2)
    rf_future = []
    if lag >= 2 and n >= lag + 3:
        X_rf, y_rf = _build_lag_features(price_arr, lag)
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_rf, y_rf)
        # Predict future step by step
        last_window = list(price_arr[-lag:])
        for _ in range(future_steps):
            pred = rf_model.predict(np.array([last_window[-lag:]]))[0]
            rf_future.append(round(float(pred), 2))
            last_window.append(pred)
    else:
        rf_future = momentum_future[:]

    # Model D: Gradient Boosting Regressor (lag features)
    gb_future = []
    if lag >= 2 and n >= lag + 3:
        X_gb, y_gb = _build_lag_features(price_arr, lag)
        gb_model = GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
        gb_model.fit(X_gb, y_gb)
        last_window_gb = list(price_arr[-lag:])
        for _ in range(future_steps):
            pred = gb_model.predict(np.array([last_window_gb[-lag:]]))[0]
            gb_future.append(round(float(pred), 2))
            last_window_gb.append(pred)
    else:
        gb_future = momentum_future[:]

    # --- 4. Accuracy backtesting (all 4 models) ---
    test_n = min(5, n // 2)
    backtest_details = []
    poly_accuracy = mom_accuracy = rf_accuracy = gb_accuracy = 0
    if test_n >= 2:
        train_prices = price_arr[:-test_n]
        true_prices = price_arr[-test_n:]
        test_times = times[-test_n:]
        nt = len(train_prices)

        # Poly model backtest
        Xt = np.arange(nt).reshape(-1, 1)
        Xt_poly = poly.fit_transform(Xt)
        bt_poly = Ridge(alpha=1.0)
        bt_poly.fit(Xt_poly, train_prices)
        Xp_test = poly.transform(np.arange(nt, nt + test_n).reshape(-1, 1))
        poly_pred_test = bt_poly.predict(Xp_test)
        poly_errors = np.abs(poly_pred_test - true_prices) / true_prices * 100
        poly_accuracy = round(100 - np.mean(poly_errors), 2)

        # Momentum model backtest
        rn2 = min(10, nt)
        rp2 = train_prices[-rn2:]
        Xr2 = np.arange(rn2).reshape(-1, 1)
        w2 = np.exp(np.linspace(0, 2, rn2))
        bt_mom = LR()
        bt_mom.fit(Xr2, rp2, sample_weight=w2)
        mom_pred_test = bt_mom.predict(np.arange(rn2, rn2 + test_n).reshape(-1, 1))
        mom_errors = np.abs(mom_pred_test - true_prices) / true_prices * 100
        mom_accuracy = round(100 - np.mean(mom_errors), 2)

        # Random Forest backtest
        rf_pred_test = np.zeros(test_n)
        if lag >= 2 and nt >= lag + 3:
            X_rf_bt, y_rf_bt = _build_lag_features(train_prices, lag)
            bt_rf = RandomForestRegressor(n_estimators=100, random_state=42)
            bt_rf.fit(X_rf_bt, y_rf_bt)
            window = list(train_prices[-lag:])
            for i in range(test_n):
                rf_pred_test[i] = bt_rf.predict(np.array([window[-lag:]]))[0]
                window.append(true_prices[i])
        else:
            rf_pred_test = mom_pred_test.copy()
        rf_errors = np.abs(rf_pred_test - true_prices) / true_prices * 100
        rf_accuracy = round(100 - np.mean(rf_errors), 2)

        # Gradient Boosting backtest
        gb_pred_test = np.zeros(test_n)
        if lag >= 2 and nt >= lag + 3:
            X_gb_bt, y_gb_bt = _build_lag_features(train_prices, lag)
            bt_gb = GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
            bt_gb.fit(X_gb_bt, y_gb_bt)
            window_gb = list(train_prices[-lag:])
            for i in range(test_n):
                gb_pred_test[i] = bt_gb.predict(np.array([window_gb[-lag:]]))[0]
                window_gb.append(true_prices[i])
        else:
            gb_pred_test = mom_pred_test.copy()
        gb_errors = np.abs(gb_pred_test - true_prices) / true_prices * 100
        gb_accuracy = round(100 - np.mean(gb_errors), 2)

        # Point-by-point backtest details
        for i in range(test_n):
            backtest_details.append({
                "time": test_times[i],
                "actual": round(float(true_prices[i]), 2),
                "poly_pred": round(float(poly_pred_test[i]), 2),
                "poly_err": round(float(poly_errors[i]), 2),
                "mom_pred": round(float(mom_pred_test[i]), 2),
                "mom_err": round(float(mom_errors[i]), 2),
                "rf_pred": round(float(rf_pred_test[i]), 2),
                "rf_err": round(float(rf_errors[i]), 2),
                "gb_pred": round(float(gb_pred_test[i]), 2),
                "gb_err": round(float(gb_errors[i]), 2)
            })

    # Best model selection
    acc_map = {'poly': poly_accuracy, 'momentum': mom_accuracy, 'rf': rf_accuracy, 'gb': gb_accuracy}
    better_model = max(acc_map, key=acc_map.get)

    # Ensemble: weighted average by accuracy
    total_acc = poly_accuracy + mom_accuracy + rf_accuracy + gb_accuracy
    if total_acc > 0:
        wp = poly_accuracy / total_acc
        wm = mom_accuracy / total_acc
        wr = rf_accuracy / total_acc
        wg = gb_accuracy / total_acc
    else:
        wp = wm = wr = wg = 0.25
    ensemble_future = [round(trend_future[i]*wp + momentum_future[i]*wm + rf_future[i]*wr + gb_future[i]*wg, 2) for i in range(future_steps)]

    # --- 5. Technical Indicators ---
    indicators = {}
    ps = pd.Series(prices)

    # RSI (14-period)
    rsi_period = min(14, n - 1)
    if rsi_period >= 2:
        delta = ps.diff()
        gain = delta.where(delta > 0, 0.0).rolling(rsi_period).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(rsi_period).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi_series = 100 - (100 / (1 + rs))
        rsi_val = round(float(rsi_series.iloc[-1]), 2) if not pd.isna(rsi_series.iloc[-1]) else None
    else:
        rsi_val = None
    indicators['rsi'] = rsi_val
    indicators['rsi_signal'] = 'Overbought' if rsi_val and rsi_val > 70 else ('Oversold' if rsi_val and rsi_val < 30 else 'Neutral')

    # Bollinger Bands (20-period, 2 std dev)
    bb_period = min(20, n)
    if bb_period >= 3:
        sma20 = ps.rolling(bb_period).mean()
        std20 = ps.rolling(bb_period).std()
        bb_upper = round(float((sma20 + 2 * std20).iloc[-1]), 2) if not pd.isna(sma20.iloc[-1]) else None
        bb_middle = round(float(sma20.iloc[-1]), 2) if not pd.isna(sma20.iloc[-1]) else None
        bb_lower = round(float((sma20 - 2 * std20).iloc[-1]), 2) if not pd.isna(sma20.iloc[-1]) else None
    else:
        bb_upper = bb_middle = bb_lower = None
    indicators['bb_upper'] = bb_upper
    indicators['bb_middle'] = bb_middle
    indicators['bb_lower'] = bb_lower
    if bb_upper and bb_lower:
        cur = prices[-1]
        indicators['bb_signal'] = 'Overbought' if cur >= bb_upper else ('Oversold' if cur <= bb_lower else 'Neutral')
    else:
        indicators['bb_signal'] = 'N/A'

    # EMA 9 & EMA 21
    ema9 = round(float(ps.ewm(span=min(9, n), adjust=False).mean().iloc[-1]), 2)
    ema21 = round(float(ps.ewm(span=min(21, n), adjust=False).mean().iloc[-1]), 2)
    indicators['ema9'] = ema9
    indicators['ema21'] = ema21
    indicators['ema_signal'] = 'Bullish' if ema9 > ema21 else ('Bearish' if ema9 < ema21 else 'Neutral')

    # MACD (12, 26, 9)
    ema12 = ps.ewm(span=min(12, n), adjust=False).mean()
    ema26 = ps.ewm(span=min(26, n), adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=min(9, n), adjust=False).mean()
    macd_val = round(float(macd_line.iloc[-1]), 2)
    signal_val = round(float(signal_line.iloc[-1]), 2)
    macd_hist = round(macd_val - signal_val, 2)
    indicators['macd'] = macd_val
    indicators['macd_signal_line'] = signal_val
    indicators['macd_histogram'] = macd_hist
    indicators['macd_signal'] = 'Bullish' if macd_val > signal_val else ('Bearish' if macd_val < signal_val else 'Neutral')

    # SuperTrend approximation (ATR-based with close-only: use abs price changes)
    st_period = min(10, n - 1)
    if st_period >= 2:
        atr_changes = ps.diff().abs().rolling(st_period).mean()
        atr_val = float(atr_changes.iloc[-1]) if not pd.isna(atr_changes.iloc[-1]) else 0
        multiplier = 3
        cur_price = prices[-1]
        st_upper = round(cur_price + multiplier * atr_val, 2)
        st_lower = round(cur_price - multiplier * atr_val, 2)
        # Trend: if price > previous supertrend lower → bullish
        prev_mid = float(ps.rolling(st_period).mean().iloc[-1]) if not pd.isna(ps.rolling(st_period).mean().iloc[-1]) else cur_price
        indicators['supertrend'] = 'Bullish' if cur_price > prev_mid else 'Bearish'
        indicators['st_upper'] = st_upper
        indicators['st_lower'] = st_lower
    else:
        indicators['supertrend'] = 'N/A'
        indicators['st_upper'] = None
        indicators['st_lower'] = None

    # Stochastic Oscillator (%K, %D)
    stoch_period = min(14, n)
    if stoch_period >= 3:
        low_min = ps.rolling(stoch_period).min()
        high_max = ps.rolling(stoch_period).max()
        denom = high_max - low_min
        denom = denom.replace(0, np.nan)
        stoch_k = ((ps - low_min) / denom * 100)
        stoch_d = stoch_k.rolling(min(3, stoch_period)).mean()
        k_val = round(float(stoch_k.iloc[-1]), 2) if not pd.isna(stoch_k.iloc[-1]) else None
        d_val = round(float(stoch_d.iloc[-1]), 2) if not pd.isna(stoch_d.iloc[-1]) else None
    else:
        k_val = d_val = None
    indicators['stoch_k'] = k_val
    indicators['stoch_d'] = d_val
    indicators['stoch_signal'] = 'Overbought' if k_val and k_val > 80 else ('Oversold' if k_val and k_val < 20 else 'Neutral')

    # Williams %R
    if stoch_period >= 3 and not pd.isna(ps.rolling(stoch_period).max().iloc[-1]):
        h_max = float(ps.rolling(stoch_period).max().iloc[-1])
        l_min = float(ps.rolling(stoch_period).min().iloc[-1])
        if h_max != l_min:
            williams_r = round((h_max - prices[-1]) / (h_max - l_min) * -100, 2)
        else:
            williams_r = None
    else:
        williams_r = None
    indicators['williams_r'] = williams_r
    indicators['williams_signal'] = 'Overbought' if williams_r is not None and williams_r > -20 else ('Oversold' if williams_r is not None and williams_r < -80 else 'Neutral')

    # CCI (Commodity Channel Index) — using close-only approximation
    cci_period = min(20, n)
    if cci_period >= 3:
        tp = ps  # typical price = close (we only have close)
        sma_tp = tp.rolling(cci_period).mean()
        mad = tp.rolling(cci_period).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
        mad = mad.replace(0, np.nan)
        cci = (tp - sma_tp) / (0.015 * mad)
        cci_val = round(float(cci.iloc[-1]), 2) if not pd.isna(cci.iloc[-1]) else None
    else:
        cci_val = None
    indicators['cci'] = cci_val
    indicators['cci_signal'] = 'Overbought' if cci_val and cci_val > 100 else ('Oversold' if cci_val and cci_val < -100 else 'Neutral')

    # ADX (Average Directional Index) — simplified with close-only
    adx_period = min(14, n - 1)
    if adx_period >= 3:
        diff_up = ps.diff()
        diff_down = -ps.diff()
        plus_dm = diff_up.where((diff_up > 0) & (diff_up > diff_down), 0.0)
        minus_dm = diff_down.where((diff_down > 0) & (diff_down > diff_up), 0.0)
        atr_adx = ps.diff().abs().rolling(adx_period).mean()
        atr_adx = atr_adx.replace(0, np.nan)
        plus_di = (plus_dm.rolling(adx_period).mean() / atr_adx * 100)
        minus_di = (minus_dm.rolling(adx_period).mean() / atr_adx * 100)
        dx_sum = (plus_di + minus_di).replace(0, np.nan)
        dx = (plus_di - minus_di).abs() / dx_sum * 100
        adx_val = round(float(dx.rolling(adx_period).mean().iloc[-1]), 2) if not pd.isna(dx.rolling(adx_period).mean().iloc[-1]) else None
    else:
        adx_val = None
    indicators['adx'] = adx_val
    indicators['adx_signal'] = 'Strong Trend' if adx_val and adx_val > 25 else ('Weak/No Trend' if adx_val else 'N/A')

    # Pivot Points (Standard: using last 2 prices as proxy for H/L/C)
    if n >= 2:
        pv_high = max(prices[-3:]) if n >= 3 else max(prices[-2:])
        pv_low = min(prices[-3:]) if n >= 3 else min(prices[-2:])
        pv_close = prices[-1]
        pivot = round((pv_high + pv_low + pv_close) / 3, 2)
        r1 = round(2 * pivot - pv_low, 2)
        s1 = round(2 * pivot - pv_high, 2)
        r2 = round(pivot + (pv_high - pv_low), 2)
        s2 = round(pivot - (pv_high - pv_low), 2)
    else:
        pivot = r1 = s1 = r2 = s2 = None
    indicators['pivot'] = pivot
    indicators['r1'] = r1
    indicators['s1'] = s1
    indicators['r2'] = r2
    indicators['s2'] = s2
    if pivot:
        indicators['pivot_signal'] = 'Bullish' if prices[-1] > pivot else ('Bearish' if prices[-1] < pivot else 'Neutral')
    else:
        indicators['pivot_signal'] = 'N/A'

    # Overall Technical Score (combine all 10 signals)
    bull_count = 0
    bear_count = 0
    for sig_key in ['rsi_signal', 'bb_signal', 'ema_signal', 'macd_signal', 'supertrend',
                     'stoch_signal', 'williams_signal', 'cci_signal', 'pivot_signal']:
        sig = indicators.get(sig_key, 'N/A')
        if sig in ('Bullish', 'Oversold'):
            bull_count += 1
        elif sig in ('Bearish', 'Overbought'):
            bear_count += 1
    total_sigs = bull_count + bear_count
    if total_sigs > 0:
        indicators['tech_score'] = round(bull_count / total_sigs * 100, 0)
    else:
        indicators['tech_score'] = 50
    indicators['overall'] = 'Strong Buy' if indicators['tech_score'] >= 80 else (
        'Buy' if indicators['tech_score'] >= 60 else (
        'Neutral' if indicators['tech_score'] >= 40 else (
        'Sell' if indicators['tech_score'] >= 20 else 'Strong Sell')))

    # --- 6. Indicator-Adjusted Predictions ---
    tech_bias = (indicators['tech_score'] - 50) / 500
    adjusted_momentum = [round(p * (1 + tech_bias * (i + 1) * 0.3), 2) for i, p in enumerate(momentum_future)]
    adjusted_poly = [round(p * (1 + tech_bias * (i + 1) * 0.2), 2) for i, p in enumerate(trend_future)]
    adjusted_rf = [round(p * (1 + tech_bias * (i + 1) * 0.25), 2) for i, p in enumerate(rf_future)]
    adjusted_gb = [round(p * (1 + tech_bias * (i + 1) * 0.25), 2) for i, p in enumerate(gb_future)]
    adjusted_ensemble = [round(p * (1 + tech_bias * (i + 1) * 0.2), 2) for i, p in enumerate(ensemble_future)]

    # Future labels
    future_labels = [f'Future +{i+1}' for i in range(future_steps)]

    # Build response arrays
    actual_prices = prices + [None] * future_steps
    smoothed_prices = smoothed + [None] * future_steps
    predicted_prices = trend_line + trend_future
    all_labels = times + future_labels
    last_updated = times[-1] if times else None

    return flask.jsonify({
        "status": "ok",
        "symbol": symbol,
        "labels": all_labels,
        "actual_prices": actual_prices,
        "smoothed_prices": smoothed_prices,
        "predicted_prices": predicted_prices,
        "current_price": prices[-1],
        "predicted_next": adjusted_ensemble[0],
        "future_prices": adjusted_momentum,
        "trend_future": adjusted_poly,
        "rf_future": adjusted_rf,
        "gb_future": adjusted_gb,
        "ensemble_future": adjusted_ensemble,
        "raw_momentum": momentum_future,
        "raw_poly": trend_future,
        "poly_accuracy": poly_accuracy,
        "momentum_accuracy": mom_accuracy,
        "rf_accuracy": rf_accuracy,
        "gb_accuracy": gb_accuracy,
        "better_model": better_model,
        "backtest": backtest_details,
        "indicators": indicators,
        "data_points": n,
        "last_updated": last_updated
    })


@app.route('/api/stock-list', methods=['GET'])
def api_stock_list():
    """Returns list of all available stock symbols from market data."""
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'market_tracker.csv')
    if not os.path.exists(csv_path):
        return flask.jsonify({"status": "error", "message": "No market data."})
    try:
        df = pd.read_csv(csv_path)
        df.columns = ['Time', 'Symbol', 'Price']
        symbols = sorted(df['Symbol'].unique().tolist())
        return flask.jsonify({"status": "ok", "symbols": symbols})
    except Exception:
        return flask.jsonify({"status": "error", "message": "Error reading market data."})


@app.route('/api/risk', methods=['GET'])
def api_risk():
    user = _get_logged_in_user()
    if not user:
        return flask.jsonify({"status": "error", "message": "No profile found. Please login and create a profile."})
    risk = get_risk_summary(user)
    return flask.jsonify({"status": "ok", "data": risk, "user": user})


@app.route('/api/portfolio', methods=['GET'])
def api_portfolio():
    user = _get_logged_in_user()
    if not user:
        return flask.jsonify({"status": "error", "message": "No profile found. Please login and create a profile."})
    risk = get_risk_summary(user)
    stocks = get_market_predictions()
    portfolio = generate_portfolio(risk['level'], risk['monthly_investable'], risk_score=risk['score'], predictions=stocks)
    return flask.jsonify({"status": "ok", "data": portfolio, "risk": risk})


@app.route('/api/advice', methods=['GET'])
def api_advice():
    user = _get_logged_in_user()
    if not user:
        return flask.jsonify({"status": "error", "message": "No profile found. Please login and create a profile."})
    risk = get_risk_summary(user)
    stocks = get_market_predictions()
    if not stocks:
        return flask.jsonify({"status": "error", "message": "No market data."})
    portfolio = generate_portfolio(risk['level'], risk['monthly_investable'], risk_score=risk['score'], predictions=stocks)
    advice = generate_ai_advice(user, risk, portfolio, stocks)
    return flask.jsonify({"status": "ok", "advice": advice})


@app.route('/api/report', methods=['GET'])
def api_report():
    user = _get_logged_in_user()
    if not user:
        return flask.jsonify({"status": "error", "message": "No profile found. Please login and create a profile."})
    risk = get_risk_summary(user)
    stocks = get_market_predictions()
    if not stocks:
        return flask.jsonify({"status": "error", "message": "No market data."})
    portfolio = generate_portfolio(risk['level'], risk['monthly_investable'], risk_score=risk['score'], predictions=stocks)
    advice = generate_ai_advice(user, risk, portfolio, stocks)
    filepath, report_text = generate_report_file(user, risk, portfolio, advice, stocks)
    return flask.jsonify({"status": "ok", "report": report_text, "file": filepath})


@app.route('/api/report/download', methods=['GET'])
def api_download_report():
    reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
    if not os.path.isdir(reports_dir):
        return flask.jsonify({"status": "error", "message": "No reports generated yet."})
    files = os.listdir(reports_dir)
    if not files:
        return flask.jsonify({"status": "error", "message": "No reports generated yet."})
    latest = max(
        [os.path.join(reports_dir, f) for f in files],
        key=os.path.getmtime
    )
    return flask.send_file(latest, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
