"""
AI Financial Advisor — Advanced Console Dashboard
Main entry point for the entire application.
"""
import os
import sys
import warnings

warnings.filterwarnings('ignore')


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    print("=" * 65)
    print("     AI FINANCIAL ADVISOR — Smart Investment Dashboard")
    print("=" * 65)
    print()


def print_menu():
    print("-" * 45)
    print("  MAIN MENU")
    print("-" * 45)
    print("  [1]  Create / Update User Profile")
    print("  [2]  Fetch Live Market Data (Yahoo)")
    print("  [3]  View Market Predictions (AI Model)")
    print("  [4]  View Risk Assessment")
    print("  [5]  View Portfolio Allocation")
    print("  [6]  Get AI Financial Advice")
    print("  [7]  Generate Full Report (Save to File)")
    print("  [8]  Run Complete Analysis (Steps 4-7)")
    print("  [0]  Exit")
    print("-" * 45)


# ===================== OPTION 1: User Profile =====================
def option_create_profile():
    clear_screen()
    print_banner()
    print("  >> CREATE / UPDATE USER PROFILE\n")
    from user_profile import collect_user_data
    collect_user_data()
    input("\n  Press Enter to continue...")


# ===================== OPTION 2: Fetch Market Data =====================
def option_fetch_market():
    clear_screen()
    print_banner()
    print("  >> FETCHING LIVE MARKET DATA\n")
    try:
        from cloud_fetcher import fetch_and_save
        fetch_and_save()
    except ImportError:
        print("  [!] cloud_fetcher.py not found!")
    except Exception as e:
        print(f"  [!] Error: {e}")
    input("\n  Press Enter to continue...")


# ===================== OPTION 3: Market Predictions =====================
def option_predictions():
    clear_screen()
    print_banner()
    print("  >> MARKET PREDICTIONS (Linear Regression)\n")

    from advisor import get_market_predictions
    stocks = get_market_predictions()

    if not stocks:
        print("  [!] Koi prediction nahi mili. Pehle market data fetch karo (Option 2).")
    else:
        print(f"  {'Symbol':<18} {'Current':<12} {'Predicted':<12} {'Action':<8}")
        print("  " + "-" * 50)
        for s in stocks:
            action_display = s['action']
            if s['action'] == 'BUY':
                action_display = 'BUY  [+]'
            elif s['action'] == 'SELL':
                action_display = 'SELL [-]'
            else:
                action_display = 'HOLD [=]'
            print(f"  {s['name']:<18} {s['current']:<12.2f} {s['predicted']:<12.2f} {action_display}")
        print(f"\n  Total {len(stocks)} stocks analyzed.")

    input("\n  Press Enter to continue...")


# ===================== OPTION 4: Risk Assessment =====================
def option_risk():
    clear_screen()
    print_banner()
    print("  >> RISK ASSESSMENT\n")

    from advisor import get_latest_user_profile
    from risk_engine import get_risk_summary

    user = get_latest_user_profile()
    if not user:
        print("  [!] User profile nahi mili. Pehle profile banao (Option 1).")
        input("\n  Press Enter to continue...")
        return None

    risk = get_risk_summary(user)

    print("  " + "=" * 45)
    print(f"  Name               : {user.get('Name', 'N/A')}")
    print(f"  Age                : {user.get('Age', 'N/A')}")
    print(f"  Monthly Income     : Rs.{float(user.get('Income', 0)):,.0f}")
    print(f"  Total Savings      : Rs.{float(user.get('Savings', 0)):,.0f}")
    print(f"  Monthly Expenses   : Rs.{float(user.get('Expenses', 0)):,.0f}")
    print("  " + "-" * 45)
    print(f"  Risk Score         : {risk['score']}/100")
    print(f"  Risk Level         : {risk['level']}")
    print(f"  Disposable Income  : Rs.{risk['disposable_income']:,.0f}")
    print(f"  Monthly Investable : Rs.{risk['monthly_investable']:,.0f}")
    print("  " + "=" * 45)

    input("\n  Press Enter to continue...")
    return risk


# ===================== OPTION 5: Portfolio Allocation =====================
def option_portfolio():
    clear_screen()
    print_banner()
    print("  >> PORTFOLIO ALLOCATION\n")

    from advisor import get_latest_user_profile
    from risk_engine import get_risk_summary
    from portfolio_generator import generate_portfolio, print_portfolio

    user = get_latest_user_profile()
    if not user:
        print("  [!] User profile nahi mili. Pehle profile banao (Option 1).")
        input("\n  Press Enter to continue...")
        return None

    risk = get_risk_summary(user)
    from advisor import get_market_predictions
    stocks = get_market_predictions()
    portfolio = generate_portfolio(risk['level'], risk['monthly_investable'], risk_score=risk['score'], predictions=stocks)
    print_portfolio(portfolio)

    input("\n  Press Enter to continue...")
    return portfolio


# ===================== OPTION 6: AI Advice =====================
def option_ai_advice():
    clear_screen()
    print_banner()
    print("  >> AI PERSONALIZED ADVICE\n")

    from advisor import get_latest_user_profile, get_market_predictions, generate_ai_advice
    from risk_engine import get_risk_summary
    from portfolio_generator import generate_portfolio

    user = get_latest_user_profile()
    if not user:
        print("  [!] User profile nahi mili. Pehle profile banao (Option 1).")
        input("\n  Press Enter to continue...")
        return

    risk = get_risk_summary(user)
    stocks = get_market_predictions()

    if not stocks:
        print("  [!] Market data nahi mili. Pehle data fetch karo (Option 2).")
        input("\n  Press Enter to continue...")
        return

    portfolio = generate_portfolio(risk['level'], risk['monthly_investable'], risk_score=risk['score'], predictions=stocks)
    print("  AI se advice le rahe hain, wait karo...\n")
    advice = generate_ai_advice(user, risk, portfolio, stocks)
    print(advice)

    input("\n  Press Enter to continue...")


# ===================== OPTION 7: Generate Report =====================
def option_generate_report():
    clear_screen()
    print_banner()
    print("  >> GENERATING FULL REPORT\n")

    from advisor import get_latest_user_profile, get_market_predictions, generate_ai_advice
    from risk_engine import get_risk_summary
    from portfolio_generator import generate_portfolio
    from report_generator import generate_report_file

    user = get_latest_user_profile()
    if not user:
        print("  [!] User profile nahi mili. Pehle profile banao (Option 1).")
        input("\n  Press Enter to continue...")
        return

    risk = get_risk_summary(user)
    stocks = get_market_predictions()

    if not stocks:
        print("  [!] Market data nahi mili. Pehle data fetch karo (Option 2).")
        input("\n  Press Enter to continue...")
        return

    portfolio = generate_portfolio(risk['level'], risk['monthly_investable'], risk_score=risk['score'], predictions=stocks)
    print("  Step 1/3: Risk Assessment done")
    print("  Step 2/3: Portfolio Generated")
    print("  Step 3/3: AI Advice generate ho rahi hai...\n")

    advice = generate_ai_advice(user, risk, portfolio, stocks)
    filepath, report_text = generate_report_file(user, risk, portfolio, advice, stocks)

    print(report_text)
    print(f"\n  Report saved: {filepath}")

    input("\n  Press Enter to continue...")


# ===================== OPTION 8: Complete Analysis =====================
def option_complete_analysis():
    clear_screen()
    print_banner()
    print("  >> COMPLETE ANALYSIS (Risk + Portfolio + AI + Report)\n")

    from advisor import get_latest_user_profile, get_market_predictions, generate_ai_advice
    from risk_engine import get_risk_summary
    from portfolio_generator import generate_portfolio, print_portfolio
    from report_generator import generate_report_file

    user = get_latest_user_profile()
    if not user:
        print("  [!] User profile nahi mili. Pehle profile banao (Option 1).")
        input("\n  Press Enter to continue...")
        return

    stocks = get_market_predictions()
    if not stocks:
        print("  [!] Market data nahi mili. Pehle data fetch karo (Option 2).")
        input("\n  Press Enter to continue...")
        return

    # Step 1: Risk
    print("  [1/4] Risk Assessment...")
    risk = get_risk_summary(user)
    print(f"         Score: {risk['score']}/100 | Level: {risk['level']}")

    # Step 2: Portfolio
    print("  [2/4] Portfolio Generation...")
    portfolio = generate_portfolio(risk['level'], risk['monthly_investable'], risk_score=risk['score'], predictions=stocks)
    print_portfolio(portfolio)

    # Step 3: AI Advice
    print("\n  [3/4] AI Advice generate ho rahi hai...")
    advice = generate_ai_advice(user, risk, portfolio, stocks)
    print("\n" + advice)

    # Step 4: Report
    print("\n  [4/4] Report save ho rahi hai...")
    filepath, _ = generate_report_file(user, risk, portfolio, advice, stocks)
    print(f"         Report saved: {filepath}")

    # Final Summary
    print("\n" + "=" * 65)
    print("  FINAL OUTPUT SUMMARY")
    print("=" * 65)
    print(f"  Risk Level       : {risk['level']} ({risk['score']}/100)")
    print(f"  Investment Plan  : Rs.{risk['monthly_investable']:,.0f}/month")
    print(f"  Expected Return  : {portfolio['expected_return']} annually")
    print(f"  Report File      : {filepath}")
    print("=" * 65)

    input("\n  Press Enter to continue...")


# ===================== MAIN LOOP =====================
def main():
    while True:
        clear_screen()
        print_banner()
        print_menu()

        choice = input("\n  Enter your choice (0-8): ").strip()

        if choice == '1':
            option_create_profile()
        elif choice == '2':
            option_fetch_market()
        elif choice == '3':
            option_predictions()
        elif choice == '4':
            option_risk()
        elif choice == '5':
            option_portfolio()
        elif choice == '6':
            option_ai_advice()
        elif choice == '7':
            option_generate_report()
        elif choice == '8':
            option_complete_analysis()
        elif choice == '0':
            clear_screen()
            print("\n  Thanks for using AI Financial Advisor! Happy Investing!\n")
            sys.exit(0)
        else:
            print("\n  [!] Invalid choice. Try again.")
            input("  Press Enter to continue...")


if __name__ == "__main__":
    main()
