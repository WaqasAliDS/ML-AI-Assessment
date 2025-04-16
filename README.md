# 📈 ML-Driven Buy/Sell Signal Generator for S&P 500 Stocks

This project builds an intelligent machine learning pipeline to generate **Buy, Sell, and Hold signals** for S&P 500 stocks using Gamma Exposure (GEX), EPS metrics, and technical indicators.

---

## 🚀 Key Features

- Predictive modeling using **XGBoost**, **Random Forest**, and **ARIMA**
- Advanced signal labeling using **Z-score of future returns**
- Feature engineering including:
  - RSI
  - SMA (Simple Moving Average)
  - MACD
  - Rolling volatility & log returns
- Accuracy comparison across models
- Signal visualization on historical prices
- Cleaned, clipped, and robust data handling

---

## 📊 Model Accuracy (Test Set)

| Ticker | XGBoost | Random Forest | ARIMA |
|--------|---------|----------------|--------|
| MSFT   | 85.17%  | **85.97%**     | 7.44%  |
| SPY    | 84.35%  | **85.76%**     | 7.57%  |
| AAPL   | 86.76%  | **87.41%**     | 7.21%  |

> ⚠️ ARIMA is included for comparison; it's univariate and underperforms in this multi-factor setup.

---

## 📁 Project Structure


---

## 🔧 How It Works

1. **Load stock-level GEX + EPS data** from CSVs or pickle.
2. **Engineer features** including GEX metrics and technical indicators (RSI, MACD, etc.).
3. **Generate labels** by calculating the Z-score of the future return.
4. **Train models** (XGBoost, Random Forest, ARIMA).
5. **Evaluate model accuracy** and visualize Buy/Sell signals on price charts.

---

## 📈 Visualizing Buy/Sell Signals

After prediction, the script overlays signals on a price chart:

- 🟢 **Buy (↑)** when signal = 2
- 🔴 **Sell (↓)** when signal = 0

This helps in **validating model performance visually**.

---

## 📦 Requirements

Install required packages:

```bash
pip install pandas numpy scikit-learn xgboost statsmodels ta matplotlib


Let me know if you want:
- A Jupyter version of the pipeline
- A command-line interface (CLI)
- Deployment script for a dashboard
