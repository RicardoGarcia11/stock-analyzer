import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.volatility import BollingerBands

st.set_page_config(page_title="Stock Analyzer", layout="wide")
st.title("📈 Personal Stock Analyzer")

# Sidebar inputs
tickers_input = st.sidebar.text_area("Enter stock tickers (comma separated)", "AAPL, MSFT, TSLA")
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))

show_sma = st.sidebar.checkbox("Show SMA (20)", True)
show_ema = st.sidebar.checkbox("Show EMA (20)", True)
show_rsi = st.sidebar.checkbox("Show RSI", True)
show_macd = st.sidebar.checkbox("Show MACD", True)
show_bbands = st.sidebar.checkbox("Show Bollinger Bands", True)

# Indicator descriptions
with st.expander("📖 Indicator Descriptions"):
    st.markdown("""
    **SMA (Simple Moving Average):** The average closing price over the last 20 days. It helps smooth out price data to identify trends.

    **EMA (Exponential Moving Average):** Similar to SMA but gives more weight to recent prices, making it more responsive to new information.

    **RSI (Relative Strength Index):** A momentum indicator that shows if a stock is overbought (>70) or oversold (<30).

    **MACD (Moving Average Convergence Divergence):** Compares short-term and long-term EMAs to identify trend direction and momentum.

    **Bollinger Bands:** Consist of a middle SMA line and two bands above and below it that measure volatility. Prices near bands can indicate overbought or oversold levels.
    """)

# Indicator interpretation guidelines
with st.expander("📊 Indicator Guidelines"):
    st.markdown("""
    ### How to interpret indicator values:
    
    - **RSI:**  
      - Above 70: Overbought (possible price drop soon)  
      - Below 30: Oversold (possible price rise soon)
      
    - **MACD:**  
      - MACD line crossing above signal line: bullish signal  
      - MACD line crossing below signal line: bearish signal
      
    - **SMA & EMA:**  
      - Price above moving averages: generally bullish trend  
      - Price below moving averages: generally bearish trend
      
    - **Bollinger Bands:**  
      - Price touching upper band: possibly overbought  
      - Price touching lower band: possibly oversold
    
    These are guidelines, not guarantees. Always consider multiple indicators and broader market context.
    """)

if not tickers:
    st.warning("Please enter at least one stock ticker.")
else:
    selected_ticker = st.sidebar.selectbox("Select ticker to view detailed charts", tickers)

    summary_data = []

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(start=start_date, end=end_date)
            if hist.empty:
                st.warning(f"No data for {ticker} in the selected date range.")
                continue

            # Indicators calculations
            hist['SMA20'] = SMAIndicator(hist['Close'], window=20).sma_indicator()
            hist['EMA20'] = EMAIndicator(hist['Close'], window=20).ema_indicator()
            rsi = RSIIndicator(hist['Close'], window=14)
            hist['RSI'] = rsi.rsi()
            macd = MACD(hist['Close'])
            hist['MACD'] = macd.macd()
            hist['MACD_signal'] = macd.macd_signal()
            bb = BollingerBands(hist['Close'])
            hist['BB_high'] = bb.bollinger_hband()
            hist['BB_low'] = bb.bollinger_lband()

            pct_change = ((hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0]) * 100

            summary_data.append({
                'Ticker': ticker,
                'Name': info.get('longName', 'N/A'),
                'Sector': info.get('sector', 'N/A'),
                'Market Cap': info.get('marketCap', np.nan),
                'Current Price': info.get('regularMarketPrice', np.nan),
                'Percent Change %': pct_change,
                'Latest RSI': hist['RSI'][-1],
                'Latest MACD': hist['MACD'][-1],
            })

        except Exception as e:
            st.warning(f"Could not load data for {ticker}: {e}")

    summary_df = pd.DataFrame(summary_data)

    if not summary_df.empty:
        st.subheader("Stock Summary")

        summary_df['Market Cap'] = summary_df['Market Cap'].apply(lambda x: f"${x/1e9:.2f}B" if pd.notna(x) else "N/A")
        summary_df['Current Price'] = summary_df['Current Price'].map('${:,.2f}'.format)
        summary_df['Percent Change %'] = summary_df['Percent Change %'].map('{:.2f}%'.format)
        summary_df['Latest RSI'] = summary_df['Latest RSI'].map('{:.2f}'.format)
        summary_df['Latest MACD'] = summary_df['Latest MACD'].map('{:.4f}'.format)

        st.dataframe(summary_df.sort_values(by='Percent Change %', ascending=False))

        # Export CSV button
        csv = summary_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Summary as CSV",
            data=csv,
            file_name='stock_summary.csv',
            mime='text/csv'
        )
    else:
        st.info("No valid stock data to display.")

    if selected_ticker:
        try:
            stock = yf.Ticker(selected_ticker)
            hist = stock.history(start=start_date, end=end_date)

            if hist.empty:
                st.warning(f"No data to display for {selected_ticker}.")
            else:
                # Recalculate indicators for selected ticker's charts
                hist['SMA20'] = SMAIndicator(hist['Close'], window=20).sma_indicator()
                hist['EMA20'] = EMAIndicator(hist['Close'], window=20).ema_indicator()
                rsi = RSIIndicator(hist['Close'], window=14)
                hist['RSI'] = rsi.rsi()
                macd = MACD(hist['Close'])
                hist['MACD'] = macd.macd()
                hist['MACD_signal'] = macd.macd_signal()
                bb = BollingerBands(hist['Close'])
                hist['BB_high'] = bb.bollinger_hband()
                hist['BB_low'] = bb.bollinger_lband()

                st.subheader(f"Detailed charts for {selected_ticker}")

                # Price chart + Bollinger Bands + SMA/EMA
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Close'))
                if show_bbands:
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['BB_high'], line=dict(color='rgba(173,216,230,0.5)'), name='Bollinger High', fill=None))
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['BB_low'], line=dict(color='rgba(173,216,230,0.5)'), name='Bollinger Low', fill='tonexty'))
                if show_sma:
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA20'], mode='lines', name='SMA20'))
                if show_ema:
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA20'], mode='lines', name='EMA20'))
                fig.update_layout(title=f"{selected_ticker} Price Chart", xaxis_title='Date', yaxis_title='Price (USD)')
                st.plotly_chart(fig, use_container_width=True)

                # RSI chart
                if show_rsi:
                    rsi_fig = go.Figure()
                    rsi_fig.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], mode='lines', name='RSI'))
                    rsi_fig.update_layout(
                        title='RSI (14)',
                        yaxis=dict(range=[0, 100]),
                        shapes=[
                            dict(type='line', y0=70, y1=70, x0=hist.index.min(), x1=hist.index.max(), line=dict(color='red', dash='dash')),
                            dict(type='line', y0=30, y1=30, x0=hist.index.min(), x1=hist.index.max(), line=dict(color='green', dash='dash'))
                        ],
                        xaxis_title='Date', yaxis_title='RSI'
                    )
                    st.plotly_chart(rsi_fig, use_container_width=True)

                # MACD chart
                if show_macd:
                    macd_fig = go.Figure()
                    macd_fig.add_trace(go.Scatter(x=hist.index, y=hist['MACD'], mode='lines', name='MACD'))
                    macd_fig.add_trace(go.Scatter(x=hist.index, y=hist['MACD_signal'], mode='lines', name='Signal'))
                    macd_fig.update_layout(title='MACD', xaxis_title='Date', yaxis_title='Value')
                    st.plotly_chart(macd_fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error loading detailed charts for {selected_ticker}: {e}")
