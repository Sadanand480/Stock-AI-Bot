"""
Risk Engine — User ka risk score calculate karta hai profile data se.
Risk Levels: Conservative, Moderate, Aggressive
"""

def calculate_risk_score(user_data):
    """
    User profile se risk score (0-100) calculate karta hai.
    Higher score = Higher risk appetite.
    """
    age = int(user_data.get('Age', 30))
    income = float(user_data.get('Income', 0))
    savings = float(user_data.get('Savings', 0))
    expenses = float(user_data.get('Expenses', 0))

    score = 0

    # --- AGE FACTOR (max 30 points) ---
    # Young = zyada risk le sakta hai
    if age < 25:
        score += 30
    elif age < 35:
        score += 25
    elif age < 45:
        score += 18
    elif age < 55:
        score += 10
    else:
        score += 5

    # --- SAVINGS-TO-INCOME RATIO (max 30 points) ---
    if income > 0:
        saving_ratio = savings / income
        if saving_ratio >= 12:
            score += 30  # 1 saal+ ki income saved
        elif saving_ratio >= 6:
            score += 22
        elif saving_ratio >= 3:
            score += 15
        elif saving_ratio >= 1:
            score += 8
        else:
            score += 3

    # --- DISPOSABLE INCOME (max 25 points) ---
    disposable = income - expenses
    if income > 0:
        disposable_ratio = disposable / income
        if disposable_ratio >= 0.5:
            score += 25
        elif disposable_ratio >= 0.3:
            score += 18
        elif disposable_ratio >= 0.15:
            score += 12
        elif disposable_ratio >= 0:
            score += 5
        else:
            score += 0  # Negative = expenses > income

    # --- INCOME LEVEL (max 15 points) ---
    if income >= 200000:
        score += 15
    elif income >= 100000:
        score += 12
    elif income >= 50000:
        score += 8
    elif income >= 25000:
        score += 5
    else:
        score += 2

    return min(score, 100)


def get_risk_level(score):
    """Score se risk level return karta hai."""
    if score >= 65:
        return "Aggressive"
    elif score >= 40:
        return "Moderate"
    else:
        return "Conservative"


def get_risk_summary(user_data):
    """Complete risk analysis return karta hai."""
    score = calculate_risk_score(user_data)
    level = get_risk_level(score)

    income = float(user_data.get('Income', 0))
    expenses = float(user_data.get('Expenses', 0))
    savings = float(user_data.get('Savings', 0))
    disposable = income - expenses

    return {
        "score": score,
        "level": level,
        "disposable_income": disposable,
        "savings": savings,
        "monthly_investable": max(disposable * 0.5, 0)  # 50% of disposable income
    }


if __name__ == "__main__":
    test_user = {"Name": "Test", "Age": 25, "Income": 50000, "Savings": 100000, "Expenses": 25000}
    result = get_risk_summary(test_user)
    print(f"Risk Score: {result['score']}/100")
    print(f"Risk Level: {result['level']}")
    print(f"Monthly Investable: ₹{result['monthly_investable']:.0f}")
