"""
Report Generator — Automatically report file banata hai with profile, risk, advice.
Saves as .txt report in /reports/ folder.
"""
import os
from datetime import datetime


def generate_report_file(user_data, risk_summary, portfolio, ai_advice, stock_predictions):
    """
    Complete report generate karke file mein save karta hai.
    Returns the file path of the saved report.
    """
    os.makedirs('reports', exist_ok=True)

    name = user_data.get('Name', 'Investor')
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"reports/report_{name}_{timestamp}.txt"

    lines = []
    lines.append("=" * 65)
    lines.append("        AI FINANCIAL ADVISOR — PERSONALIZED REPORT")
    lines.append("=" * 65)
    lines.append(f"  Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  For       : {name}")
    lines.append("")

    # --- SECTION 1: USER PROFILE ---
    lines.append("-" * 65)
    lines.append("  SECTION 1: USER PROFILE")
    lines.append("-" * 65)
    lines.append(f"  Name           : {name}")
    lines.append(f"  Age            : {user_data.get('Age', 'N/A')}")
    lines.append(f"  Monthly Income : Rs.{float(user_data.get('Income', 0)):,.0f}")
    lines.append(f"  Total Savings  : Rs.{float(user_data.get('Savings', 0)):,.0f}")
    lines.append(f"  Monthly Expense: Rs.{float(user_data.get('Expenses', 0)):,.0f}")
    lines.append("")

    # --- SECTION 2: RISK ASSESSMENT ---
    lines.append("-" * 65)
    lines.append("  SECTION 2: RISK ASSESSMENT")
    lines.append("-" * 65)
    lines.append(f"  Risk Score          : {risk_summary['score']}/100")
    lines.append(f"  Risk Level          : {risk_summary['level']}")
    lines.append(f"  Disposable Income   : Rs.{risk_summary['disposable_income']:,.0f}")
    lines.append(f"  Monthly Investable  : Rs.{risk_summary['monthly_investable']:,.0f}")
    lines.append("")

    # --- SECTION 3: PORTFOLIO ALLOCATION ---
    lines.append("-" * 65)
    lines.append("  SECTION 3: PORTFOLIO ALLOCATION")
    lines.append("-" * 65)
    lines.append(f"  Strategy        : {portfolio['description']}")
    lines.append(f"  Expected Return : {portfolio['expected_return']} annually")
    lines.append("")
    lines.append(f"  {'Category':<20} {'%':<10} {'Amount (Rs.)':<15}")
    lines.append("  " + "-" * 45)
    for cat, det in portfolio['allocation'].items():
        lines.append(f"  {cat:<20} {det['percentage']}%{'':<7} {det['amount']:>10,.0f}")
    lines.append("")
    lines.append(f"  Recommended Stocks : {', '.join(portfolio['stock_picks'])}")
    lines.append(f"  Recommended ETFs   : {', '.join(portfolio['etf_picks'])}")
    lines.append("")

    # --- SECTION 4: AI ADVICE ---
    lines.append("-" * 65)
    lines.append("  SECTION 4: AI PERSONALIZED ADVICE")
    lines.append("-" * 65)
    lines.append("")
    lines.append(ai_advice)
    lines.append("")

    # --- FOOTER ---
    lines.append("=" * 65)
    lines.append("  Disclaimer: This advice is AI-generated. Please consult")
    lines.append("  a certified financial advisor before making investments.")
    lines.append("=" * 65)

    report_text = "\n".join(lines)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report_text)

    return filename, report_text


if __name__ == "__main__":
    # Test
    user = {"Name": "Test", "Age": 25, "Income": 50000, "Savings": 100000, "Expenses": 25000}
    risk = {"score": 70, "level": "Aggressive", "disposable_income": 25000, "monthly_investable": 12500}
    portfolio = {
        "description": "High growth", "expected_return": "15-22%",
        "allocation": {"Stocks": {"percentage": 50, "amount": 6250},
                       "Mutual Funds": {"percentage": 25, "amount": 3125},
                       "ETFs": {"percentage": 15, "amount": 1875},
                       "Fixed Deposit": {"percentage": 10, "amount": 1250}},
        "stock_picks": ["RELIANCE.BO", "TCS.BO"],
        "etf_picks": ["NIFTYBEES.NS"]
    }
    stocks = [{"name": "RELIANCE.BO", "current": 1394.3, "predicted": 1400, "action": "BUY"}]
    advice = "Bhai, invest karo!"

    path, text = generate_report_file(user, risk, portfolio, advice, stocks)
    print(f"Report saved: {path}")
    print(text)
