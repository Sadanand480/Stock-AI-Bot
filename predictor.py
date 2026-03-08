import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import warnings

# Terminal warnings ko hide karne ke liye
warnings.filterwarnings('ignore')

def train_and_predict():
    print("\n[AI BRAIN] Loading Market Data and Training Models...\n")
    
    try:
        # CSV Load karna (Header ke sath)
        df = pd.read_csv('market_tracker.csv')
        
        # Columns ke naam standardise kar rahe hain (agar header mismatch ho)
        df.columns = ['Time', 'Symbol', 'Price']
        
        # Prices ko numbers mein convert karna
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df = df.dropna()

    except Exception as e:
        print("[!] Error: market_tracker.csv nahi mili ya format galat hai.")
        return

    # Table Header
    print(f"{'Symbol':<15} | {'Current Price':<15} | {'Predicted (AI)':<15} | {'Action':<10}")
    print("-" * 65)

    # Har Stock (Symbol) ke liye alag Model Train karna
    for symbol, group in df.groupby('Symbol'):
        prices = group['Price'].values
        
        # Agar 5 se kam entries hain toh accuracy kharab hogi, isliye skip
        if len(prices) < 5:
            continue
            
        # X (Time Step) aur Y (Actual Price) define karna
        X = np.arange(len(prices)).reshape(-1, 1)
        y = prices
        
        # --- MODEL TRAINING ---
        model = LinearRegression()
        model.fit(X, y)
        
        # --- PREDICTION ---
        next_time_step = np.array([[len(prices)]])
        prediction = model.predict(next_time_step)[0]
        
        current_price = prices[-1]
        
        # Simple Logic
        if prediction > current_price:
            action = "BUY 📈"
        elif prediction < current_price:
            action = "SELL 📉"
        else:
            action = "HOLD ⏸"
            
        print(f"{symbol:<15} | {current_price:<15.2f} | {prediction:<15.2f} | {action}")
        
    print("=" * 65)

if __name__ == "__main__":
    train_and_predict()