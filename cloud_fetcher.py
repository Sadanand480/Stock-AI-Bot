import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# ===================== MEGA STOCK LIST =====================
symbols = [
    # --- BANKING & FINANCE ---
    "HDFCBANK.BO", "ICICIBANK.BO", "SBIN.BO", "AXISBANK.BO", "KOTAKBANK.BO",
    "BAJFINANCE.BO", "CHOLAFIN.BO", "PFC.BO", "RECLTD.BO", "MUTHOOTFIN.BO",
    # --- IT SECTOR ---
    "TCS.BO", "INFY.BO", "HCLTECH.BO", "WIPRO.BO", "TECHM.BO", 
    "PERSISTENT.BO", "COFORGE.BO", "KPITTECH.BO", "TATAELXSI.BO",
    # --- FMCG & CONSUMPTION ---
    "HINDUNILVR.BO", "ITC.BO", "NESTLEIND.BO", "BRITANNIA.BO", "TATACONSUM.BO",
    "VBL.BO", "DABUR.BO", "MARICO.BO", "COLPAL.BO", "TITAN.BO",
    # --- AUTO & ENERGY ---
    "MARUTI.BO", "M&M.BO", "RELIANCE.BO", "ONGC.BO",
    "NTPC.BO", "POWERGRID.BO", "ADANIGREEN.BO", "TATASTEEL.BO", "JINDALSTEL.BO",
    # --- ETFs (Safe Investing) ---
    "NIFTYBEES.NS", "BANKBEES.NS", "GOLDBEES.NS", "SILVERBEES.NS", "ITBEES.NS",
    "PHARMABEES.NS", "MON100.NS", "MAFANG.NS", "MID150BEES.NS", "JUNIORBEES.NS"
]

def fetch_and_save():
    # Indian market hours check (9:15 AM - 3:30 PM IST, Mon-Fri)
    now_dt = datetime.now()
    now = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    current_minutes = now_dt.hour * 60 + now_dt.minute
    market_open = 9 * 60 + 15   # 9:15 AM
    market_close = 15 * 60 + 30  # 3:30 PM
    is_weekday = now_dt.weekday() < 5  # Mon=0 to Fri=4

    if not is_weekday or current_minutes < market_open or current_minutes > market_close:
        print(f"Market band hai ({now}). Data fetch skip kiya.")
        return

    new_rows = []
    
    print(f"Fetching data for {len(symbols)} stocks...")
    
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            # Live price nikalna
            price = ticker.fast_info['last_price']
            if price:
                new_rows.append({"Time": now, "Symbol": sym, "Price": round(price, 2)})
        except Exception as e:
            print(f"Error fetching {sym}: {e}")

    df_new = pd.DataFrame(new_rows)
    file_name = 'market_tracker.csv'

    # CSV update logic
    if os.path.exists(file_name):
        df_old = pd.read_csv(file_name)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_final = df_new

    df_final.to_csv(file_name, index=False)
    print(f"Successfully saved data for {len(new_rows)} stocks.")

if __name__ == "__main__":
    fetch_and_save()
