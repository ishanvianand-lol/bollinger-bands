import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

st.set_page_config(layout="wide") 

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

col1, col2 = st.columns([2,5])


with st.sidebar:
    stock_symbol = st.text_input("Enter a Stock Symbol").upper()
    start_date = st.date_input('Start Date')
    end_date = st.date_input('End Date')
    initial_capital = st.number_input(
        'Enter Initial Capital',
        min_value=0, 
        value=10000
    )


with col2:
    if (end_date - start_date).days < 30:
        st.warning('Can\'t depict SMAs') 
        st.stop()


    # validating input
    if not stock_symbol or stock_symbol.strip() == "":
        st.warning("Please enter a valid stock symbol.")
        st.stop()

    # when valid
    ticker = yf.Ticker(stock_symbol)

    # Fetch Data
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

    # Relative Strength Index
    change_delta = stock_data['Close'].diff()
    up = change_delta.clip(lower = 0)
    down = -1*change_delta.clip(upper = 0)

    emaUP = up.ewm(com=13, adjust=False).mean()
    emaDOWN = down.ewm(com=13, adjust=False).mean()

    rs = emaUP / emaDOWN
    stock_data['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    stock_data['MACD'] = stock_data['EMA_12'] - stock_data['EMA_26']
    stock_data['Signal Line'] = stock_data['MACD'].ewm(span=9, adjust=False).mean()
    stock_data['MACD Histogram'] = stock_data['MACD'] - stock_data['Signal Line']

    # MA50 to check the bull/bear/choppy market
    stock_data['MA50'] = stock_data['Close'].rolling(50).mean() # will use this data whilst buying and selling

    stock_data = stock_data.dropna(subset=
                                    ["Upper Band", "Lower Band", "RSI",
                                    "MACD", "Signal Line"]
                                ).copy()

    # strong selling and buying signals
    lower_trend_moved = (stock_data['Close'] < stock_data['Lower Band'])
    upper_trend_moved = (stock_data['Close'] > stock_data['Upper Band'])

    rsi_condition_buy = stock_data['RSI'] < 35
    rsi_condition_sell = stock_data['RSI'] > 70

    bullish_macd = (
        (stock_data['MACD'] > stock_data['Signal Line']) &
        (stock_data['MACD'].shift(1) <= stock_data['Signal Line'].shift(1))
    )
    bearish_macd = (
        (stock_data['MACD'] < stock_data['Signal Line']) &
        (stock_data['MACD'].shift(1) >= stock_data['Signal Line'].shift(1))
    )

    stock_data['Strong_Buy'] = (
        lower_trend_moved &
        (rsi_condition_buy | 
            bullish_macd)
    ).astype(int)

    stock_data['Strong_Sell'] = (
        upper_trend_moved &
        (rsi_condition_sell |
        bearish_macd)
    ).astype(int)

    # less strict conditions for lesser risk
    band_width = stock_data['Upper Band'] - stock_data['Lower Band']
    band_position = (stock_data['Close'] - stock_data['Lower Band']) / band_width

    lower_trend_moved = (band_position <= 0.15)
    upper_trend_moved = (band_position >= 0.97)

    rsi_condition_buy = stock_data['RSI'] < 40 
    rsi_condition_sell = stock_data['RSI'] > 60 

    bullish_macd = (stock_data['MACD'] > stock_data['Signal Line'])
    bearish_macd = (stock_data['MACD'] < stock_data['Signal Line'])


    stock_data['Buy'] = (
        lower_trend_moved | rsi_condition_buy | bullish_macd
    ).astype(int)

    stock_data['Sell'] = (
        upper_trend_moved | rsi_condition_sell | bearish_macd
    ).astype(int)

    custom_style = mpf.make_mpf_style(
        base_mpf_style='binance',  # Clean base style
        rc={'font.size': 15},
        gridcolor='lightgray',
        facecolor='white',
        figcolor='white'
    )

    add_plots = [
        mpf.make_addplot(stock_data["Upper Band"], color="lightgray"),
        mpf.make_addplot(stock_data["Lower Band"], color="lightgray"),
        mpf.make_addplot(stock_data["SMA20"], color="#FF72E0"),
        mpf.make_addplot(stock_data['MA50'], color = "#0A57FF"),
        mpf.make_addplot(stock_data['RSI'], panel=1, title='RSI', color = "orange"),
        mpf.make_addplot(stock_data['MACD'], panel=2, title='MACD', color = "blue"),
        mpf.make_addplot(stock_data['Signal Line'], panel=2, color = "pink"),
        mpf.make_addplot(stock_data["MACD Histogram"], type='bar', panel=2, color='grey', alpha=0.35),

    ]

    buy_points = stock_data[stock_data['Buy'] == 1]
    if not buy_points.empty:
        buy_markers = pd.Series(index=stock_data.index, dtype=float)
        buy_markers.loc[buy_points.index] = stock_data.loc[buy_points.index, "Close"]
        
        add_plots.append(
            mpf.make_addplot(
                buy_markers,
                type='scatter',
                marker="^",
                color="#74ac68",
                markersize=16
            )
        )

    sell_points = stock_data[stock_data['Sell'] == 1]
    if not sell_points.empty:
        sell_marker = pd.Series(index=stock_data.index, dtype=float)
        sell_marker.loc[sell_points.index] = stock_data.loc[sell_points.index, "Close"]
        
        add_plots.append(
            mpf.make_addplot(
                sell_marker,
                type='scatter',
                marker="v",
                color="#a44040",
                markersize=16
            )
        )

    fig, ax = mpf.plot(
        stock_data,
        type="candle",
        addplot=add_plots,
        returnfig=True,
        figsize=(15, 7),
        style=custom_style,
        title=f"{stock_symbol} - Signals",
        ylabel="Price",
        panel_ratios=(3, 1, 2)  # taller price panel, smaller RSI/MACD panels
    )

    st.pyplot(fig)
    plt.clf()

with col1:
    # Initialize tracking variables
    cash = initial_capital
    shares = 0
    portfolio_values = []
    trades = []

    # Go through each row
    for index, row in stock_data.iterrows():
        date = index
        price = row['Close']
        ma50 = row['MA50']
        if price > ma50 * 1.05:  # Price 5% above MA
            market_regime = "BULL"
            
        elif price < ma50 * 0.95:  # Price 5% below MA
            market_regime = "BEAR"
            
        else:
            market_regime = "NEUTRAL"

        # Check for Strong Buy
        if row['Strong_Buy'] == 1 and cash > 0:
            if market_regime == 'BULL':
                amount_to_invest = cash * 0.6
            elif market_regime == 'BEAR': 
                amount_to_invest = cash * 0.4
            else:
                amount_to_invest = cash * 0.5


            shares_to_buy = amount_to_invest / price
            cash -= amount_to_invest
            shares += shares_to_buy
            trades.append({
                'Date': date, 
                'Action': 'Buy',
                'Price': price,
                'Shares': shares_to_buy,
                'Amount': amount_to_invest,
                'Cash': cash,
                'Total Shares': shares
            })
        
        # Check for Buy
        elif row['Buy'] == 1 and cash > 0:
            if market_regime == 'BULL': 
                amount_to_invest = cash * 0.5
                shares_to_buy = amount_to_invest / price
                cash -= amount_to_invest
                shares += shares_to_buy
                trades.append({
                    'Date': date, 
                    'Action': 'Buy',
                    'Price': price,
                    'Shares': shares_to_buy,
                    'Amount': amount_to_invest,
                    'Cash': cash,
                    'Total Shares': shares
                })

        # Check for Strong Sell
        elif row['Strong_Sell'] == 1 and shares > 0:
            if market_regime == 'BULL': 
                shares_to_sell = shares * 0.3
            elif market_regime == 'BEAR': 
                shares_to_sell = shares * 0.6
            else: 
                shares_to_sell = shares * 0.45

            cash += shares_to_sell * price
            shares -= shares_to_sell
            trades.append({
                'Date': date, 
                'Action': 'Strong Sell',
                'Price': price,
                'Shares': shares_to_sell,
                'Amount': shares_to_sell * price,
                'Cash': cash,
                'Total Shares': shares
            })
        
        # Check for Sell
        elif row['Sell'] == 1 and shares > 0:
            if market_regime == 'BEAR': 
                shares_to_sell = shares * 0.5
                cash += shares_to_sell * price
                shares = shares - shares_to_sell
                trades.append({
                    'Date': date, 
                    'Action': 'Strong Sell',
                    'Price': price,
                    'Shares': shares_to_sell,
                    'Amount': shares_to_sell * price,
                    'Cash': cash,
                    'Total Shares': shares
                })
            
        # Calculate portfolio value for this day
        portfolio_value = cash + (shares * price)
        portfolio_values.append(portfolio_value)


    trades_df = pd.DataFrame(trades)
    portfolio_df = pd.DataFrame()
    portfolio_df['Portfolio_Value'] = portfolio_values
    
    final_value = portfolio_df['Portfolio_Value'].iloc[-1]
    total_profit = final_value - initial_capital
    profit_pct = (total_profit / initial_capital) * 100
    
    # Display
    st.subheader("📊 Portfolio Summary")
    st.metric("Initial Capital", f"${initial_capital:,.2f}")
    st.metric("Final Value", f"${final_value:,.2f}")
    st.metric("Profit/Loss", f"${total_profit:,.2f}", f"{profit_pct:.2f}%")
    
    st.subheader("💼 Current Holdings")
    st.write(f"Cash: ${cash:,.2f}")
    st.write(f"Shares: {shares:.2f}")
    
st.subheader("📈 Trade History")
if not trades_df.empty:
    st.dataframe(trades_df)
else:
    st.write("No trades executed")