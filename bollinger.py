import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

st.set_page_config(layout="wide") # Optional: Use wide layout for more horizontal space

# Inject custom CSS to reduce top padding
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 5rem;
        padding-bottom: 10rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1,3])

with col2:
    tab1, tab2, tab3, tab4 = st.tabs(['Buy/Sell', 'Bollinger Bands', 'RSI', 'MACD'])

    with st.sidebar:
        stock_symbol = st.text_input("Enter a Stock Symbol").upper()
        start_date = st.date_input('Start Date')
        end_date = st.date_input('End Date')
        initial_capital = st.number_input('Enter Initial Capital',
        min_value=0, value=10000)

    if (end_date - start_date).days < 20:
        st.warning('Can\'t depict SMAs') 
        st.stop()


    # validate input
    if not stock_symbol or stock_symbol.strip() == "":
        st.warning("Please enter a valid stock symbol.")
        st.stop()

    # when valid
    ticker = yf.Ticker(stock_symbol)

    # --- Fetch Data ---
    stock_data = ticker.history(
        interval="1d",
        start=start_date,
        end=end_date
    )

    if stock_data.empty:
        st.error("No data available for this stock / date range.")
        st.stop()


    # Calculate Bollinger Bands
    stock_data["SMA20"] = stock_data["Close"].rolling(20).mean()
    std20 = stock_data["Close"].rolling(20).std()

    stock_data["Upper Band"] = stock_data["SMA20"] + 2 * std20
    stock_data["Lower Band"] = stock_data["SMA20"] - 2 * std20

    stock_data['EMA_12'] = stock_data['Close'].ewm(span=12, adjust=False).mean()
    stock_data['EMA_26'] = stock_data['Close'].ewm(span=26, adjust=False).mean()

    plot_df = stock_data.dropna(subset=['Upper Band'])

    with tab2:
        add_plot = [
            mpf.make_addplot(plot_df["Upper Band"], color="grey"),
            mpf.make_addplot(plot_df["Lower Band"], color="grey"),
            mpf.make_addplot(plot_df["SMA20"], color="blue", width=0.5),
        ]

        st.subheader("Bollinger Bands")

        fig, ax = mpf.plot(
            plot_df,
            type="candle",
            style="yahoo",
            addplot=add_plot,
            returnfig=True,
            figsize=(14, 7)
        )

        st.pyplot(fig)
        plt.clf()



    with tab3:
        # Relative Strength Index
        change_delta = plot_df['Close'].diff()
        up = change_delta.clip(lower = 0)
        down = -1*change_delta.clip(upper = 0)

        emaUP = up.ewm(com=13, adjust=False).mean()
        emaDOWN = down.ewm(com=13, adjust=False).mean()

        rs = emaUP / emaDOWN
        plot_df['RSI'] = 100 - (100 / (1 + rs))
        
        st.subheader("Relative Strength Index")

        plt.figure(figsize=(14, 6)) 
        plt.plot(
            plot_df["RSI"],
            color='blue'
        )
        plt.axhline(70, color='red', linestyle='--', linewidth=1)
        plt.axhline(30, color='green', linestyle='--', linewidth=1)
        plt.title('Relative Strength Index for ' + stock_symbol)
        plt.ylim(0,100)
        plt.legend()
        st.pyplot(plt.gcf())
        plt.clf()

    with tab4:
        st.subheader("Moving Average Convergence Divergence")

        # MACD
        stock_data['MACD Line'] = stock_data['EMA_12'] - stock_data['EMA_26']
        stock_data['Signal Line'] = stock_data['MACD Line'].ewm(span=9, adjust=False).mean()
        stock_data['MACD Histogram'] = stock_data['MACD Line'] - stock_data['Signal Line']

        plt.figure(figsize=(14, 7))
        plt.plot(stock_data['MACD Line'], label='MACD Line', color='blue')
        plt.plot(stock_data['Signal Line'], label='Signal Line', color='red')
        plt.bar(stock_data.index, stock_data['MACD Histogram'], label='MACD Histogram', color='grey')
        plt.title('Moving Average Convergence Divergence for ' + stock_symbol)
        plt.legend()

        st.pyplot(plt.gcf())
        plt.clf()


    # selling and buying signals

    newPlot = pd.DataFrame(index=stock_data.index)
    newPlot['Close'] = stock_data["Close"]
    newPlot['Lower Band'] = stock_data["Lower Band"]
    newPlot['Upper Band'] = stock_data["Upper Band"]
    newPlot['RSI'] = plot_df['RSI']
    newPlot['MACD'] = stock_data['MACD Line']

    lower_trend_moved = (
        (newPlot['Close'].shift(1) >= newPlot['Lower Band'].shift(1)) &
        (newPlot['Close'] < newPlot['Lower Band'])
    )

    upper_trend_moved = (
        (newPlot['Close'].shift(1) <= newPlot['Upper Band'].shift(1)) &
        (newPlot['Close'] > newPlot['Upper Band'])
    )


    newPlot['Buy'] = (
        lower_trend_moved &
        (newPlot['RSI'] < 30) &
        (newPlot['MACD'] > 0)
    ).astype(int)

    newPlot['Sell'] = (
        upper_trend_moved &
        (newPlot['RSI'] > 70) &
        (newPlot['MACD'] < 0)
    ).astype(int)



with col1:
    st.metric('Portfolio', 10)