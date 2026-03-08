import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# 1. Data Load karo
df = pd.read_csv('market_tracker.csv')
stock_df = df[df['Symbol'] == 'RELIANCE.BO'].copy()

# 2. Target banao (1 = Buy, 0 = Sell)
stock_df['Target'] = (stock_df['Price'].shift(-1) > stock_df['Price']).astype(int)

# 3. Features aur Target alag karo
X = stock_df[['Price']] # Tu yahan Volume bhi add kar sakta hai
y = stock_df['Target']

# 4. Train/Test split aur Model fit
X_train, X_test, y_train, y_test = train_test_split(X[:-1], y[:-1], test_size=0.2)
rf_model = RandomForestClassifier(n_estimators=100)
rf_model.fit(X_train, y_train)

print("Random Forest Train ho gaya!")