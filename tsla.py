import yfinance as yf
import matplotlib.pyplot as plt

def run():
    ticker = 'TSLA'
    data = yf.download(ticker, start='2023-01-01', end='2025-06-24')

    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['STD20'] = data['Close'].rolling(window=20).std()
    data['UpperBB'] = data['MA20'] + 2 * data['STD20']
    data['LowerBB'] = data['MA20'] - 2 * data['STD20']

    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), sharex=True)

    ax1.plot(data['Close'], label='Close Price')
    ax1.plot(data['MA20'], label='20-day MA')
    ax1.plot(data['UpperBB'], label='Upper BB', linestyle='--')
    ax1.plot(data['LowerBB'], label='Lower BB', linestyle='--')
    ax1.set_title(f'{ticker} Price and Bollinger Bands')
    ax1.legend()

    ax2.plot(data['RSI'], label='RSI', color='orange')
    ax2.axhline(70, color='red', linestyle='--')
    ax2.axhline(30, color='green', linestyle='--')
    ax2.set_title('RSI')
    ax2.legend()

    ax3.plot(data['MACD'], label='MACD', color='blue')
    ax3.plot(data['Signal'], label='Signal Line', color='red')
    ax3.set_title('MACD')
    ax3.legend()

    plt.xlabel('Date')
    plt.show()
