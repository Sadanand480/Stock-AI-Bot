import pandas as pd
import numpy as np
from groq import Groq
from sklearn.linear_model import LinearRegression
import os
from dotenv import load_dotenv

# .env file se API key load karo (SAFE METHOD)
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_latest_user_profile():
    file_path = 'user_profile.csv'

    if not os.path.exists(file_path):
        print(f"[!] {file_path} nahi mili!")
        return None

    try:
        df = pd.read_csv(file_path, on_bad_lines='skip')
        data = df.iloc[-1].to_dict()
        return data
    except Exception as e:
        print(f"[!] Error reading CSV: {e}")
        return None


def get_market_predictions():
    """market_tracker.csv se predictions generate karta hai (Linear Regression)."""
    try:
        df = pd.read_csv('market_tracker.csv')
        df.columns = ['Time', 'Symbol', 'Price']
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df = df.dropna()
    except Exception:
        return []

    results = []
    for symbol, group in df.groupby('Symbol'):
        prices = group['Price'].values
        if len(prices) < 3:
            continue

        X = np.arange(len(prices)).reshape(-1, 1)
        y = prices

        model = LinearRegression()
        model.fit(X, y)

        prediction = model.predict(np.array([[len(prices)]]))[0]
        current_price = prices[-1]

        if prediction > current_price:
            action = "BUY"
        elif prediction < current_price:
            action = "SELL"
        else:
            action = "HOLD"

        results.append({
            "name": symbol,
            "current": round(current_price, 2),
            "predicted": round(prediction, 2),
            "action": action
        })

    return results


def generate_ai_advice(user, risk_summary, portfolio, stocks):
    """Groq AI se personalized financial advice leta hai."""
    try:
        name     = user.get('Name', 'Investor')
        age      = user.get('Age', 'N/A')
        income   = user.get('Income', 0)
        savings  = user.get('Savings', 0)
        expenses = user.get('Expenses', 0)

        user_context = (f"User: {name}, Age: {age}, "
                        f"Income: Rs.{income}, Savings: Rs.{savings}, "
                        f"Expenses: Rs.{expenses}")

        risk_context = (f"Risk Score: {risk_summary['score']}/100, "
                        f"Risk Level: {risk_summary['level']}, "
                        f"Disposable Income: Rs.{risk_summary['disposable_income']:.0f}, "
                        f"Monthly Investable: Rs.{risk_summary['monthly_investable']:.0f}")

        alloc_lines = ""
        for cat, det in portfolio['allocation'].items():
            alloc_lines += f"  - {cat}: {det['percentage']}% (Rs.{det['amount']:,.0f})\n"

        stock_list = ""
        # Send only the user's recommended stocks + ETFs (unique to their score)
        recommended = portfolio.get('stock_details', []) + portfolio.get('etf_details', [])
        if recommended:
            for s in recommended:
                stock_list += f"- {s['name']}: Current Rs.{s['current']}, Predicted Rs.{s['predicted']} -> {s['action']} ({s.get('change_pct', 0)}% change)\n"
        else:
            for s in stocks[:10]:
                stock_list += f"- {s['name']}: Current Rs.{s['current']}, Predicted Rs.{s['predicted']} -> {s['action']}\n"

        prompt = f"""
You are a Senior Indian Financial Advisor. Analyze this profile and give personalized advice in simple, easy-to-understand English. Write as if explaining to someone who has never invested before. Do NOT use Hindi, Hinglish, or any slang like 'Bhai'. Use plain English only.

USER PROFILE:
{user_context}

RISK ASSESSMENT:
{risk_context}

PORTFOLIO ALLOCATION (AI Generated):
{alloc_lines}
Expected Return: {portfolio['expected_return']}

RECOMMENDED INVESTMENTS (Picked specifically for this user based on their risk score of {risk_summary['score']}/100):
{stock_list}

TASK:
1. Evaluate the user's financial health in 2-3 sentences — mention specific numbers from their profile (income, savings, expenses).
2. From the RECOMMENDED INVESTMENTS above, pick the top 5 and explain in 1 simple line each why this user should BUY, SELL, or HOLD.
3. Comment on the portfolio allocation percentages — are they right for THIS specific user given their age ({age}), income (Rs.{income}), and risk score ({risk_summary['score']})?
4. Give 3-4 actionable tips that are SPECIFIC to this user's situation — mention their exact numbers.
5. Use simple, clear English. If you use a finance term, explain it in brackets.
6. Keep it concise — max 400 words.
7. Do NOT give generic advice. Every sentence should relate to THIS user's specific numbers and situation.
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        if "429" in str(e):
            return "[!] Bhai, API limit khatam! 1 minute baad try karna."
        return f"[!] Error: {e}"


if __name__ == "__main__":
    from risk_engine import get_risk_summary
    from portfolio_generator import generate_portfolio, print_portfolio

    user = get_latest_user_profile()
    if user:
        risk = get_risk_summary(user)
        stocks = get_market_predictions()
        portfolio = generate_portfolio(risk['level'], risk['monthly_investable'], risk_score=risk['score'], predictions=stocks)

        print_portfolio(portfolio)
        print("\nAI Advice generate ho rahi hai...\n")
        print(generate_ai_advice(user, risk, portfolio, stocks))