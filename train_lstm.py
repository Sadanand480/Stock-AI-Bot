import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout

# 1. Data Load karo
df = pd.read_csv('market_tracker.csv')

# Sirf ek stock select karo training ke liye (e.g., RELIANCE.BO)
stock_df = df[df['Symbol'] == 'RELIANCE.BO']['Price'].values.reshape(-1, 1)

# 2. Scaling (0 se 1 ke beech)
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(stock_df)

# 3. Sequences banao (Pichle 10 prices se agla 1 predict karna)
X, y = [], []
for i in range(10, len(scaled_data)):
    X.append(scaled_data[i-10:i, 0])
    y.append(scaled_data[i, 0])

X, y = np.array(X), np.array(y)

# --- SAFETY CHECK & MODEL TRAINING ---
if len(X) == 0:
    print("Bhai, data bahut kam hai! market_tracker.csv mein kam se kam 11 rows chahiye.")
else:
    # Reshape sirf tabhi hoga jab data available ho
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    # 4. LSTM Model Build karo (Ab ye 'else' ke andar hai)
    model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)),
        Dropout(0.2),
        LSTM(units=50),
        Dropout(0.2),
        Dense(units=1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')
    
    # 5. Train karo
    print("Training shuru ho rahi hai...")
    model.fit(X, y, epochs=25, batch_size=32)

    # Save karo model
    model.save('stock_model.h5')
    print("Model Train ho gaya bhai aur 'stock_model.h5' save ho gayi!")