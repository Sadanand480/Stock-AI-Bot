"""
Portfolio Generator — Dynamic allocation based on exact risk score + real market predictions.
Har user ka portfolio UNIQUE hota hai uski income, savings, expenses ke hisaab se.
"""


def _calculate_dynamic_allocation(risk_score):
    """
    Risk score (0-100) se EXACT allocation calculate karta hai.
    Score 0 = most conservative, Score 100 = most aggressive.
    Har score ka allocation alag hoga — koi 2 users ka same nahi hoga
    agar unka risk score alag hai.
    """
    # Linear interpolation between conservative (score=0) and aggressive (score=100)
    # Conservative anchor: Stocks=5, MF=15, ETF=30, FD=50
    # Aggressive anchor:   Stocks=60, MF=25, ETF=10, FD=5
    t = risk_score / 100.0  # 0.0 to 1.0

    stocks_pct = round(5 + t * 55)       # 5% → 60%
    mf_pct     = round(15 + t * 10)      # 15% → 25%
    etf_pct    = round(30 - t * 20)      # 30% → 10%
    fd_pct     = 100 - stocks_pct - mf_pct - etf_pct  # remainder goes to FD

    # Clamp FD so it's never negative
    if fd_pct < 0:
        fd_pct = 0
        total = stocks_pct + mf_pct + etf_pct
        stocks_pct = round(stocks_pct / total * 100)
        mf_pct = round(mf_pct / total * 100)
        etf_pct = 100 - stocks_pct - mf_pct

    return {
        "Stocks": stocks_pct,
        "Mutual Funds": mf_pct,
        "ETFs": etf_pct,
        "Fixed Deposit": fd_pct
    }


def _get_expected_return(risk_score):
    """Risk score se expected annual return range."""
    if risk_score >= 80:
        return "18-25%"
    elif risk_score >= 65:
        return "14-20%"
    elif risk_score >= 50:
        return "11-16%"
    elif risk_score >= 35:
        return "8-13%"
    elif risk_score >= 20:
        return "6-10%"
    else:
        return "4-7%"


def _get_strategy_description(risk_score, risk_level):
    """Dynamic strategy description based on exact score."""
    if risk_score >= 75:
        return f"{risk_level} ({risk_score}/100) — Maximum growth focus, high volatility acceptable."
    elif risk_score >= 55:
        return f"{risk_level} ({risk_score}/100) — Growth-oriented with some stability cushion."
    elif risk_score >= 40:
        return f"{risk_level} ({risk_score}/100) — Balanced approach, moderate risk tolerance."
    elif risk_score >= 25:
        return f"{risk_level} ({risk_score}/100) — Safety-focused with small growth component."
    else:
        return f"{risk_level} ({risk_score}/100) — Capital preservation priority, minimal risk."


def _pick_stocks_from_predictions(predictions, risk_score):
    """
    Real market predictions se stocks pick karta hai based on EXACT risk score.
    Different scores = different stock picks, even within same risk level.
    Uses score to control: count, sort strategy, and offset into the list.
    """
    if not predictions:
        return [], []

    # Separate stocks and ETFs
    stocks = []
    etfs = []
    for p in predictions:
        name = p['name']
        current = p['current']
        predicted = p['predicted']
        change_pct = ((predicted - current) / current * 100) if current > 0 else 0
        entry = {**p, 'change_pct': round(change_pct, 2)}

        if name.endswith('.NS'):
            etfs.append(entry)
        else:
            stocks.append(entry)

    # Sort stocks by predicted change %
    stocks.sort(key=lambda x: x['change_pct'], reverse=True)
    etfs.sort(key=lambda x: x['change_pct'], reverse=True)

    # How many picks — varies with exact score
    stock_count = max(3, min(len(stocks), 4 + round(risk_score / 20)))  # 4 to ~9
    etf_count = max(2, min(len(etfs), 7 - round(risk_score / 30)))     # 3 to ~7

    # Use exact score to create an offset so different scores pick different stocks
    # Score 65 offset=0, score 75 offset=2, score 85 offset=4, etc.
    score_offset = (risk_score % 30) // 6  # gives 0-4 range of offset

    if risk_score >= 65:
        # Aggressive: Growth stocks but offset by exact score
        start = min(score_offset, max(0, len(stocks) - stock_count))
        picked_stocks = stocks[start:start + stock_count]
        # ETFs also offset
        etf_start = min(score_offset % 3, max(0, len(etfs) - etf_count))
        picked_etfs = etfs[etf_start:etf_start + etf_count]
    elif risk_score >= 40:
        # Moderate: Mix — some growth + some stable, ratio depends on exact score
        growth_ratio = (risk_score - 40) / 25.0  # 0.0 to 1.0 within moderate range
        growth_count = max(1, round(stock_count * growth_ratio))
        stable_count = stock_count - growth_count
        growth = stocks[score_offset:score_offset + growth_count]
        stable_sorted = sorted(stocks, key=lambda x: abs(x['change_pct']))
        stable = [s for s in stable_sorted if s not in growth][:stable_count]
        picked_stocks = growth + stable
        picked_etfs = etfs[score_offset % 2:score_offset % 2 + etf_count]
    else:
        # Conservative: Most stable stocks, offset by score
        stable_sorted = sorted(stocks, key=lambda x: abs(x['change_pct']))
        start = min(score_offset, max(0, len(stable_sorted) - stock_count))
        picked_stocks = stable_sorted[start:start + stock_count]
        safe_etfs = sorted(etfs, key=lambda x: abs(x['change_pct']))
        picked_etfs = safe_etfs[:etf_count]

    return picked_stocks, picked_etfs


def generate_portfolio(risk_level, monthly_investable, risk_score=50, predictions=None):
    """
    Dynamic portfolio generate karta hai.
    - risk_score: exact 0-100 score (har user ka different)
    - predictions: actual market predictions list from advisor.py
    """
    alloc_pcts = _calculate_dynamic_allocation(risk_score)

    stock_picks, etf_picks = _pick_stocks_from_predictions(predictions or [], risk_score)

    portfolio = {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "monthly_investable": monthly_investable,
        "expected_return": _get_expected_return(risk_score),
        "description": _get_strategy_description(risk_score, risk_level),
        "allocation": {},
        "stock_picks": [s['name'] for s in stock_picks],
        "etf_picks": [e['name'] for e in etf_picks],
        "stock_details": stock_picks,
        "etf_details": etf_picks
    }

    for category in ["Stocks", "Mutual Funds", "ETFs", "Fixed Deposit"]:
        pct = alloc_pcts[category]
        amount = round(monthly_investable * pct / 100, 2)
        portfolio["allocation"][category] = {
            "percentage": pct,
            "amount": amount
        }

    return portfolio


def print_portfolio(portfolio):
    """Portfolio ko console pe display karta hai."""
    print("\n" + "=" * 60)
    print("         PORTFOLIO ALLOCATION PLAN")
    print("=" * 60)
    print(f"  Risk Level      : {portfolio['risk_level']}")
    print(f"  Risk Score      : {portfolio.get('risk_score', 'N/A')}/100")
    print(f"  Monthly Invest  : Rs.{portfolio['monthly_investable']:,.0f}")
    print(f"  Expected Return : {portfolio['expected_return']} annually")
    print(f"  Strategy        : {portfolio['description']}")
    print("-" * 60)

    print(f"\n  {'Category':<20} {'Allocation':<15} {'Amount (Rs.)':<15}")
    print("  " + "-" * 50)
    for cat, details in portfolio["allocation"].items():
        print(f"  {cat:<20} {details['percentage']}%{'':<12} {details['amount']:>10,.0f}")

    if portfolio.get('stock_details'):
        print(f"\n  Recommended Stocks ({len(portfolio['stock_details'])}):")
        for s in portfolio['stock_details']:
            arrow = "+" if s['change_pct'] >= 0 else ""
            print(f"    {s['name']:<18} {s['action']:<5} ({arrow}{s['change_pct']}%)")

    if portfolio.get('etf_details'):
        print(f"\n  Recommended ETFs ({len(portfolio['etf_details'])}):")
        for e in portfolio['etf_details']:
            arrow = "+" if e['change_pct'] >= 0 else ""
            print(f"    {e['name']:<18} {e['action']:<5} ({arrow}{e['change_pct']}%)")

    print("=" * 60)


if __name__ == "__main__":
    # Test with dummy predictions
    test_preds = [
        {"name": "RELIANCE.BO", "current": 1365, "predicted": 1350, "action": "SELL"},
        {"name": "TCS.BO", "current": 2618, "predicted": 2600, "action": "SELL"},
        {"name": "HDFCBANK.BO", "current": 879, "predicted": 875, "action": "SELL"},
        {"name": "NIFTYBEES.NS", "current": 281, "predicted": 280, "action": "SELL"},
        {"name": "GOLDBEES.NS", "current": 137, "predicted": 140, "action": "BUY"},
    ]
    # Conservative user (score=30)
    print("\n--- CONSERVATIVE USER (Score 30) ---")
    p1 = generate_portfolio("Conservative", 5000, risk_score=30, predictions=test_preds)
    print_portfolio(p1)

    # Aggressive user (score=80)
    print("\n--- AGGRESSIVE USER (Score 80) ---")
    p2 = generate_portfolio("Aggressive", 25000, risk_score=80, predictions=test_preds)
    print_portfolio(p2)
