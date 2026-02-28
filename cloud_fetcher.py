import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# Wahi stocks jo tere C++ project mein hain
symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "SBIN.NS"] 

def fetch_and_save():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_rows = []
    
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            # Live price nikalna
            price = ticker.fast_info['last_price']
            new_rows.append({"Time": now, "Symbol": sym, "Price": round(price, 2)})
        except:
            print(f"Error fetching {sym}")

    df_new = pd.DataFrame(new_rows)
    file_name = 'market_tracker.csv'

    # Agar file pehle se hai toh niche naya data jodo
    if os.path.exists(file_name):
        df_old = pd.read_csv(file_name)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_final = df_new

    df_final.to_csv(file_name, index=False)
    print(f"Success! Saved data for {len(symbols)} stocks.")

if __name__ == "__main__":
    fetch_and_save()
