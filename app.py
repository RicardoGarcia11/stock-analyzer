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

import plotly.graph_objs as go

st.markdown("## 📈 Index Trend Chart")

fig = go.Figure()

for symbol, name in indices.items():
    df = yf.download(symbol, start=start_date, end=today)
    if not df.empty and "Close" in df.columns:
        df["Normalized"] = df["Close"] / df["Close"].iloc[0]  # Normalize to start at 1
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["Normalized"],
            mode='lines',
            name=name
        ))

fig.update_layout(
    title="Normalized Index Price Trends",
    xaxis_title="Date",
    yaxis_title="Normalized Price (Start = 1)",
    legend_title="Index",
    height=500
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("## 🚀 Top Tech Stocks Trend Chart")

fig_stocks = go.Figure()

for ticker in top_tickers:
    df = yf.download(ticker, start=start_date, end=today)
    if not df.empty and "Close" in df.columns:
        df["Normalized"] = df["Close"] / df["Close"].iloc[0]
        fig_stocks.add_trace(go.Scatter(
            x=df.index,
            y=df["Normalized"],
            mode='lines',
            name=ticker
        ))

fig_stocks.update_layout(
    title="Normalized Top Tech Stocks Price Trends",
    xaxis_title="Date",
    yaxis_title="Normalized Price (Start = 1)",
    legend_title="Ticker",
    height=500
)

st.plotly_chart(fig_stocks, use_container_width=True)

# ETFs
sector_etfs = {
    "Technology": "XLK",
    "Health Care": "XLV",
    "Financials": "XLF",
    "Consumer Discretionary": "XLY",
    "Industrials": "XLI",
    "Energy": "XLE",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Materials": "XLB",
    "Communication Services": "XLC"
}

st.markdown("## 🏭 Sector ETF Performance")

sector_data = []

for sector, ticker in sector_etfs.items():
    df = yf.download(ticker, start=start_date, end=today)
    if not df.empty and "Close" in df.columns:
        try:
            start_price = df["Close"].iloc[0].item()
            end_price = df["Close"].iloc[-1].item()
            pct_change = ((end_price - start_price) / start_price) * 100
            sector_data.append({
                "Sector": sector,
                "Ticker": ticker,
                "Start Price": f"${start_price:,.2f}",
                "End Price": f"${end_price:,.2f}",
                "Change (%)": f"{pct_change:+.2f}%"
            })
        except:
            pass

if sector_data:
    df_sector = pd.DataFrame(sector_data).sort_values(by="Change (%)", ascending=False)
    st.dataframe(df_sector, use_container_width=True)
else:
    st.warning("No sector ETF data available for the selected timeframe.")

# Heatmap
import plotly.express as px

if sector_data:
    df_sector = pd.DataFrame(sector_data)
    # Convert Change (%) strings like '+3.45%' to float
    df_sector["Change (%)"] = df_sector["Change (%)"].str.replace("%", "").astype(float)

    fig_heatmap = px.imshow(
        df_sector[["Change (%)"]].T,
        x=df_sector["Sector"],
        y=["Change (%)"],
        color_continuous_scale="RdYlGn",
        text_auto=True,
        aspect="auto",
        title="Sector Performance Heatmap"
    )

    fig_heatmap.update_layout(
        yaxis=dict(showticklabels=True),
        xaxis_title="Sector",
        yaxis_title="",
        coloraxis_colorbar=dict(title="% Change")
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)
