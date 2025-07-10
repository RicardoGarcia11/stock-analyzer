import streamlit as st

st.set_page_config(page_title="Market Overview", layout="wide")

st.title("🏠 Market Overview")

st.markdown("Use the sidebar to filter by timeframe and explore top performing stocks.")

# Placeholder for filter (you’ll implement this in detail soon)
timeframe = st.selectbox("Select Timeframe", ["1W", "1M", "YTD", "1Y"])

# Placeholder for indices comparison
st.markdown("### 📈 Index Comparison")
st.markdown("Here you'll see performance of NASDAQ, S&P500, etc.")

# Placeholder for top stocks
st.markdown("### 🚀 Top Performing Stocks")
st.write("Table or chart of top stocks in selected timeframe will go here.")
