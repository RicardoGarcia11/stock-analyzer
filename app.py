import streamlit as st
import yfinance as yf
import plotly.graph_objs as go

st.set_page_config(page_title="Stock Analyzer", layout="wide")
st.title("📈 Personal Stock Analyzer")

# Input
ticker = st.text_input("Enter stock ticker:", "AAPL")

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1y")

        st.subheader("Company Info")
        st.write(info.get('longName', 'N/A'))
        st.write(f"Sector: {info.get('sector', 'N/A')}")
        st.write(f"Market Cap: ${info.get('marketCap', 0):,}")
        st.write(f"Current Price: ${info.get('regularMarketPrice', 0):.2f}")

        st.subheader("Price Chart")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name='Close'))
        fig.update_layout(title='1-Year Close Price', xaxis_title='Date', yaxis_title='Price (USD)')
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error fetching data: {e}")
