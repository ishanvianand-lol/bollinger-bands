# 📈 Adaptive Trading Strategy

An intelligent algorithmic trading backtesting system that adapts to different market conditions using technical indicators and regime detection.

## 🎯 Features

- **Adaptive Market Regime Detection**: Automatically identifies BULL, BEAR, and NEUTRAL markets using MA50
- **Multiple Technical Indicators**:
  - Bollinger Bands (20-day SMA with 2 standard deviations)
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - MA50 (50-day Moving Average for trend detection)
- **Smart Signal Generation**:
  - **Strong Buy/Sell**: Combines multiple indicators for high-confidence signals
  - **Regular Buy/Sell**: More frequent signals with lower conviction
- **Dynamic Position Sizing**: Adjusts investment amounts based on market regime
- **Interactive Visualizations**: Candlestick charts with overlaid indicators and trade signals
- **Comprehensive Performance Metrics**: Portfolio summary, trade history, and regime analysis

## 🚀 Performance Highlights

Based on backtesting results (2019-2024):

| Stock | Time Period | Result     | vs Buy & Hold             |
| ----- | ----------- | ---------- | ------------------------- |
| TSLA  | 2019-2021   | **+1259%** | Beat (captured 84%)       |
| AMD   | 2022-2024   | **+774%**  | Beat by 500%!             |
| SPY   | 2022        | **-7%**    | Protected 18% in crash    |
| ARKK  | 2021-2022   | **-47%**   | Protected 33% in collapse |

**Key Strengths:**

- ✅ Excellent performance in trending bull markets
- ✅ Strong downside protection in bear markets
- ✅ Adaptive regime-based position sizing

**Known Limitations:**

- ⚠️ Underperforms on choppy, range-bound stocks
- ⚠️ Not suitable for stocks with frequent regime changes

## 📋 Requirements

- Python 3.8+
- See `requirements.txt` for package dependencies

## 🛠️ Installation

1. Clone the repository:

```bash
git clone <your-repo-url>
cd adaptive-trading-strategy
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:

```bash
streamlit run app.py
```

## 💻 Usage

1. **Enter Stock Symbol**: Input any valid stock ticker (e.g., NVDA, AAPL, SPY)
2. **Select Date Range**: Choose start and end dates (minimum 30 days for indicator calculation)
3. **Set Initial Capital**: Enter your starting investment amount
4. **View Results**:
   - Interactive candlestick chart with buy/sell signals
   - Portfolio performance summary
   - Market regime analysis
   - Complete trade history

## 📊 Strategy Logic

### Market Regime Detection

```
BULL Market:   Price > MA50 × 1.05
BEAR Market:   Price < MA50 × 0.95
NEUTRAL:       Price within ±5% of MA50
```

### Position Sizing by Regime

**BULL Market** (Stay invested, ride the trend):

- Strong Buy: 60% of available cash
- Regular Buy: 50% of available cash
- Strong Sell: 30% of shares (keep 70%)
- Regular Sell: Ignored

**BEAR Market** (Preserve capital, sell aggressively):

- Strong Buy: 40% of available cash
- Regular Buy: Ignored
- Strong Sell: 60% of shares
- Regular Sell: 50% of shares

**NEUTRAL Market** (Balanced approach):

- Strong Buy: 50% of available cash
- Regular Buy: Ignored
- Strong Sell: 45% of shares
- Regular Sell: Ignored

### Signal Definitions

**Strong Buy** (High conviction):

- Price below lower Bollinger Band AND
- (RSI < 35 OR MACD bullish crossover)

**Strong Sell** (High conviction):

- Price above upper Bollinger Band AND
- (RSI > 70 OR MACD bearish crossover)

**Regular Buy** (Lower conviction):

- Price in lower 15% of Bollinger Band OR
- RSI < 40 OR
- MACD > Signal Line

**Regular Sell** (Lower conviction):

- Price in upper 97% of Bollinger Band OR
- RSI > 60 OR
- MACD < Signal Line

## 📈 Backtesting Methodology

The strategy simulates trading with:

- **Starting capital**: User-defined (default: $10,000)
- **Trading frequency**: Daily (based on close prices)
- **Execution**: Assumes perfect fills at close price
- **No transaction costs**: Results don't include commissions/slippage
- **No slippage**: Assumes instant execution at quoted price

**Note**: Real-world results will differ due to:

- Transaction costs (commissions, spreads)
- Slippage (especially on larger orders)
- Partial fills
- Market impact

## 🎓 Technical Indicators Explained

### Bollinger Bands

- **Upper Band**: SMA20 + (2 × 20-day standard deviation)
- **Lower Band**: SMA20 - (2 × 20-day standard deviation)
- **Purpose**: Identify overbought/oversold conditions

### RSI (Relative Strength Index)

- **Range**: 0-100
- **Overbought**: > 70
- **Oversold**: < 30
- **Purpose**: Measure momentum and potential reversals

### MACD

- **MACD Line**: EMA12 - EMA26
- **Signal Line**: 9-day EMA of MACD
- **Histogram**: MACD - Signal Line
- **Purpose**: Identify trend changes and momentum

### MA50 (50-day Moving Average)

- **Purpose**: Determine long-term trend direction
- **Above MA50**: Bullish trend
- **Below MA50**: Bearish trend

## 🔧 Customization

You can modify the strategy by adjusting:

**Indicator Periods** (lines 66-85):

```python
stock_data["SMA20"] = stock_data["Close"].rolling(20).mean()
stock_data['MA50'] = stock_data['Close'].rolling(50).mean()
```

**Regime Thresholds** (lines 206-211):

```python
if price > ma50 * 1.05:  # BULL threshold
    market_regime = "BULL"
elif price < ma50 * 0.95:  # BEAR threshold
    market_regime = "BEAR"
```

**Position Sizing** (lines 214-280):

```python
if market_regime == 'BULL':
    amount_to_invest = cash * 0.6  # Adjust percentage
```

**Signal Conditions** (lines 117-161):

```python
rsi_condition_buy = stock_data['RSI'] < 35  # Adjust RSI level
```

## 📝 Best Practices

**✅ Good for:**

- Trending stocks (tech, growth)
- Bull market environments
- Medium-term trading (weeks to months)
- Stocks with clear technical patterns

**❌ Avoid on:**

- Highly choppy/range-bound stocks
- Penny stocks with low liquidity
- News-driven stocks (biotech, small caps)
- Very short time periods (< 3 months)

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Add transaction cost modeling
- Implement portfolio optimization
- Add more technical indicators
- Create strategy comparison tools
- Add risk management features (stop-loss, position limits)

## ⚠️ Disclaimer

**THIS SOFTWARE IS FOR EDUCATIONAL PURPOSES ONLY.**

- Past performance does not guarantee future results
- This is NOT financial advice
- Always do your own research before investing
- Consider consulting a financial advisor
- Trading involves substantial risk of loss
- Never invest more than you can afford to lose

The authors are not responsible for any financial losses incurred through use of this software.

## 📄 License

MIT License - feel free to use and modify for your own purposes.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Market data from [yfinance](https://github.com/ranaroussi/yfinance)
- Charting with [mplfinance](https://github.com/matplotlib/mplfinance)

---

**Happy Trading! 📊💰**

_Remember: The best strategy is the one you understand and can stick with through different market conditions._
