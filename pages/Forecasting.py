import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import plotly.graph_objs as go

st.set_page_config(page_title="Stock Forecasting", layout="wide")
st.title("🔮 Stock Price Forecasting")

# --- User inputs
ticker = st.text_input("Enter Stock Ticker (e.g. AAPL)", value="AAPL").upper()

forecast_days = st.slider("Days to Forecast", min_value=5, max_value=60, value=15)

# --- Date range for historical data
end_date = datetime.today()
start_date = end_date - timedelta(days=365)  # last 1 year

# --- Fetch historical data
df = yf.download(ticker, start=start_date, end=end_date)

if df.empty:
    st.error(f"No data found for ticker {ticker}")
else:
    st.markdown(f"### Historical Closing Prices for {ticker}")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='Actual Close'
    ))

    # --- Moving Average Forecast
    window = 10
    df['MA_Forecast'] = df['Close'].rolling(window).mean().shift(1)

    # Forecast next days with MA (simple approach)
    last_ma = df['MA_Forecast'].iloc[-1]
    ma_forecast_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=forecast_days)
    ma_forecast_values = [last_ma] * forecast_days

    # --- Linear Regression Forecast
    df_lr = df.reset_index()
    df_lr['Date_Ordinal'] = df_lr['Date'].map(datetime.toordinal)
    lr = LinearRegression()
    X = df_lr[['Date_Ordinal']]
    y = df_lr['Close']
    lr.fit(X, y)

    future_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=forecast_days)
    future_dates_ordinal = future_dates.map(datetime.toordinal).to_numpy().reshape(-1,1)
    lr_forecast_values = lr.predict(future_dates_ordinal)

    # Plot forecasts
    fig.add_trace(go.Scatter(
        x=ma_forecast_dates,
        y=ma_forecast_values,
        mode='lines',
        name='Moving Average Forecast'
    ))

    fig.add_trace(go.Scatter(
        x=future_dates,
        y=lr_forecast_values,
        mode='lines',
        name='Linear Regression Forecast'
    ))

    fig.update_layout(
        title=f"{ticker} Price Forecast",
        xaxis_title="Date",
        yaxis_title="Price",
        legend_title="Legend",
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)
