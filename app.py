import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(page_title="Market Overview", layout="wide")
st.title("🏠 Market Overview")

# --- Timeframe filter
timeframe_option = st.selectbox("Select Timeframe", ["1W", "1M", "YTD", "1Y"])

today = datetime.date.today()

if timeframe_option == "1W":
    start_date = today - datetime.timedelta(days=7)
elif timeframe_option == "1M":
    start_date = today - datetime.timedelta(days=30)
elif timeframe_option == "YTD":
    start_date = datetime.date(today.year, 1, 1)
elif timeframe_option == "1Y":
    start_date = today - datetime.timedelta(days=365)
else:
    start_date = today - datetime.timedelta(days=30)

# --- Index symbols (Yahoo Finance tickers)
indices = {
    "^GSPC": "S&P 500",
    "^IXIC": "NASDAQ",
    "^DJI": "Dow Jones"
}

st.markdown("## 📈 Major Indices Performance")
index_data = []

for symbol, name in indices.items():
    df = yf.download(symbol, start=start_date, end=today)
    if not df.empty and "Close" in df.columns:
        try:
            start_price = df["Close"].iloc[0].item()
            end_price = df["Close"].iloc[-1].item()
            pct_change = ((end_price - start_price) / start_price) * 100
            index_data.append({
                "Index": name,
                "Start Price": f"${start_price:,.2f}",
                "End Price": f"${end_price:,.2f}",
                "Change (%)": f"{pct_change:+.2f}%"
            })
        except:
            pass

if index_data:
    st.dataframe(pd.DataFrame(index_data), use_container_width=True)
else:
    st.warning("No index data available for the selected timeframe.")

# --- Top stocks to compare (e.g., Big Tech)
top_tickers = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA"]
st.markdown("## 🚀 Top Tech Stock Performance")

stock_data = []

for ticker in top_tickers:
    df = yf.download(ticker, start=start_date, end=today)
    if not df.empty and "Close" in df.columns:
        try:
            start_price = df["Close"].iloc[0].item()
            end_price = df["Close"].iloc[-1].item()
            pct_change = ((end_price - start_price) / start_price) * 100
            stock_data.append({
                "Ticker": ticker,
                "Start Price": f"${start_price:,.2f}",
                "End Price": f"${end_price:,.2f}",
                "Change (%)": f"{pct_change:+.2f}%"
            })
        except:
            pass

if stock_data:
    df_stock = pd.DataFrame(stock_data).sort_values(by="Change (%)", ascending=False)
    st.dataframe(df_stock, use_container_width=True)
else:
    st.warning("No stock data available for the selected timeframe.")
