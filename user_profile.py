import csv
import os

def collect_user_data():
    print("--- 🏦 Welcome to AI Financial Advisor ---")
    print("Please enter your details to get a personalized report:\n")

    # User inputs
    name = input("Enter Your Name: ")
    age = int(input("Enter Your Age: "))
    income = float(input("Enter Monthly Income (₹): "))
    savings = float(input("Enter Total Savings (₹): "))
    expenses = float(input("Enter Monthly Expenses (₹): "))

    # Data ko ek dictionary mein save karte hain
    user_data = {
        "Name": name,
        "Age": age,
        "Income": income,
        "Savings": savings,
        "Expenses": expenses
    }

    # CSV file mein save karna (advisor isi file ko read karega)
    file_exists = os.path.isfile('user_profile.csv')
    
    with open('user_profile.csv', 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=user_data.keys())
        if not file_exists:
            writer.writeheader()  # Pehli baar header banayega
        writer.writerow(user_data)

    print(f"\n✅ Done Sir/Mam {name} your profile Created Successfully!")

if __name__ == "__main__":
    collect_user_data()