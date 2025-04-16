# -*- coding: utf-8 -*-
"""AAPL.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Qf5fDD_4RZ6xU_XrxzeuwDXHpHFbryU5
"""

import pickle
import pandas as pd

def load_pickle_to_dataframe(file_path):
    """Load a pickle file and return its DataFrame."""
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
        if isinstance(data, pd.DataFrame):
            return data
        else:
            raise TypeError(f"Expected DataFrame, got {type(data)}")


# --- MAIN EXECUTION ---

file_path = 'NetGEX_AbsGEX_EPS(AAPL).pickle'

try:
    AAPL_df = load_pickle_to_dataframe(file_path)

except Exception as e:
    print(f"❌ Error: {e}")

AAPL_df

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import accuracy_score
import ta

# --- STEP 1: Load Data ---
df = AAPL_df.copy()

# --- STEP 2: Feature Engineering ---
# Add Technical Indicators
df['rsi'] = ta.momentum.RSIIndicator(close=df['Spot_Close']).rsi()
df['sma_10'] = ta.trend.SMAIndicator(close=df['Spot_Close'], window=10).sma_indicator()
df['macd'] = ta.trend.MACD(close=df['Spot_Close']).macd()
df['log_return'] = np.log(df['Spot_Close'] / df['Spot_Close'].shift(1))
df['rolling_std'] = df['log_return'].rolling(window=10).std()
df['rolling_mean'] = df['log_return'].rolling(window=10).mean()

# GEX features to keep
feature_cols = [
    'PCT_EPS_1mo_Open', 'PCT_EPS_1mo_Close',
    'PCT_EPS_1mo_High', 'PCT_EPS_1mo_Low',
    'open_abs_gex', 'close_abs_gex', 'volume_abs_gex',
    'open_net_gex', 'close_net_gex', 'volume_net_gex',
    'rsi', 'sma_10', 'macd', 'log_return', 'rolling_std', 'rolling_mean'
]

# --- STEP 3: Label Generation with Z-Score ---
df['future_return'] = df['Spot_Close'].shift(-10) / df['Spot_Close'] - 1
zscore = (df['future_return'] - df['future_return'].mean()) / df['future_return'].std()
df['signal'] = np.where(zscore > 1, 1, np.where(zscore < -1, -1, 0))

# --- STEP 4: Drop NaNs created by indicators or return shifts ---
df.dropna(subset=feature_cols + ['signal'], inplace=True)

# --- STEP 5: Prepare Features and Labels ---
X = df[feature_cols]
label_map = {-1: 0, 0: 1, 1: 2}
df['mapped_signal'] = df['signal'].map(label_map)
y = df['mapped_signal']

# --- STEP 6: Train/Test Split ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, test_size=0.25, random_state=42
)

# --- STEP 7: Clean & Clip ---
for X_part in [X_train, X_test]:
    X_part.replace([np.inf, -np.inf], np.nan, inplace=True)
    X_part.fillna(X_part.median(), inplace=True)
    X_part.clip(lower=-1e6, upper=1e6, inplace=True)

# --- STEP 8: XGBoost Model ---
xgb_model = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
xgb_model.fit(X_train, y_train)
xgb_pred = xgb_model.predict(X_test)

# --- STEP 9: Random Forest Model ---
rf_model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)

# --- STEP 10: ARIMA Model (Univariate on Spot_Close) ---
arima_series = df['Spot_Close']
arima_diff = arima_series.diff().dropna()
arima_model = ARIMA(arima_diff[:5000], order=(5, 1, 0))
arima_result = arima_model.fit()
arima_forecast = arima_result.forecast(steps=len(y_test))

arima_signal = np.sign(arima_forecast.values)
arima_signal_mapped = np.where(arima_signal == -1, 0, np.where(arima_signal == 0, 1, 2))
aligned_y_test = y_test[:len(arima_signal_mapped)]

# --- STEP 11: Accuracy Comparison ---
xgb_acc = accuracy_score(y_test, xgb_pred)
rf_acc = accuracy_score(y_test, rf_pred)
arima_acc = accuracy_score(aligned_y_test, arima_signal_mapped)

results = pd.DataFrame({
    'Model': ['XGBoost', 'Random Forest', 'ARIMA'],
    'Accuracy': [xgb_acc, rf_acc, arima_acc]
})

print("\n📊 Model Comparison:")
print(results)

import matplotlib.pyplot as plt

# Map predictions back to their corresponding timestamps
# Instead of using iloc, use .loc to access rows by their labels
pred_df = df.loc[X_test.index].copy()
pred_df['predicted_signal'] = xgb_pred

# Filter Buy and Sell points
buy_signals = pred_df[pred_df['predicted_signal'] == 2]
sell_signals = pred_df[pred_df['predicted_signal'] == 0]

# --- PLOT ---
plt.figure(figsize=(15, 6))
plt.plot(pred_df['Spot_Close'], label='Spot_Close', color='blue', alpha=0.5)

# Overlay Buy and Sell
plt.scatter(buy_signals.index, buy_signals['Spot_Close'], label='Buy Signal', color='green', marker='^', s=60)
plt.scatter(sell_signals.index, sell_signals['Spot_Close'], label='Sell Signal', color='red', marker='v', s=60)

plt.title('Buy/Sell Signals on Spot_Close')
plt.xlabel('Timestamp')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

