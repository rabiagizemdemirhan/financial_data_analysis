import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os

def run_technical_analysis_for_multiple_tickers(tickers_list):
    start_date = '2023-01-01'
    end_date = '2025-06-24'

    output_folder = 'technical_analysis_charts'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"'{output_folder}' folder created.")

    for ticker in tickers_list:
        print(f"\nDownloading data and performing analysis for {ticker}...")
        try:
            data = yf.download(ticker, start=start_date, end=end_date)

            if data.empty:
                print(f"No data found or downloaded for {ticker}. Skipping...")
                continue

            # Calculate Bollinger Bands
            data['MA20'] = data['Close'].rolling(window=20).mean()
            data['STD20'] = data['Close'].rolling(window=20).std()
            data['UpperBB'] = data['MA20'] + 2 * data['STD20']
            data['LowerBB'] = data['MA20'] - 2 * data['STD20']

            # Calculate RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss.replace(0, 1e-9)
            data['RSI'] = 100 - (100 / (1 + rs))

            # Calculate MACD
            exp1 = data['Close'].ewm(span=12, adjust=False).mean()
            exp2 = data['Close'].ewm(span=26, adjust=False).mean()
            data['MACD'] = exp1 - exp2
            data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

            # Plotting
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
            fig.suptitle(f'{ticker} Technical Analysis (2023-2025)', fontsize=16)

            # Price and Bollinger Bands
            ax1.plot(data['Close'], label='Close Price', color='blue')
            ax1.plot(data['MA20'], label='20-day MA', color='orange')
            ax1.plot(data['UpperBB'], label='Upper BB', linestyle='--', color='red')
            ax1.plot(data['LowerBB'], label='Lower BB', linestyle='--', color='green')
            ax1.set_title('Price and Bollinger Bands')
            ax1.legend()
            ax1.grid(True, linestyle='--', alpha=0.6)

            # RSI
            ax2.plot(data['RSI'], label='RSI', color='purple')
            ax2.axhline(70, color='red', linestyle='--', label='Overbought (70)')
            ax2.axhline(30, color='green', linestyle='--', label='Oversold (30)')
            ax2.set_title('Relative Strength Index (RSI)')
            ax2.legend()
            ax2.grid(True, linestyle='--', alpha=0.6)

            # MACD
            ax3.plot(data['MACD'], label='MACD Line', color='blue')
            ax3.plot(data['Signal'], label='Signal Line', color='red')
            ax3.set_title('Moving Average Convergence Divergence (MACD)')
            ax3.legend()
            ax3.grid(True, linestyle='--', alpha=0.6)

            plt.xlabel('Date')
            plt.tight_layout(rect=[0, 0.03, 1, 0.96])

            # Save the chart to a file
            filename = os.path.join(output_folder, f'{ticker}_technical_analysis.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"'{ticker}' technical analysis chart saved as '{filename}'.")
            plt.close(fig) # Close the figure to prevent it from displaying

        except Exception as e:
            print(f"An error occurred for ticker {ticker}: {e}")

# List of tickers to analyze
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA']

# Phase 1: Technical Analysis Charts (Saved to files)
run_technical_analysis_for_multiple_tickers(tickers)

print("\n--- Starting General Portfolio Analysis ---")

# Phase 2: General Portfolio Analysis (Console Output and Charts Saved to Files)
# Download data (all tickers at once)
data_all_tickers = yf.download(tickers, start='2023-01-01', end='2025-06-24')['Close']

# Calculate log returns
log_returns = np.log(data_all_tickers / data_all_tickers.shift(1))

# Basic statistics
stats = pd.DataFrame({
    'Mean': log_returns.mean(),
    'StdDev': log_returns.std(),
    'Skewness': log_returns.skew(),
    'Kurtosis': log_returns.kurtosis()
})

print("\nBasic Statistics:")
print(stats)

# Create folder for general analysis charts
general_charts_folder = 'general_portfolio_charts'
if not os.path.exists(general_charts_folder):
    os.makedirs(general_charts_folder)
    print(f"'{general_charts_folder}' folder created.")

# Volatility chart (annualized)
annual_volatility = log_returns.std() * np.sqrt(252)

plt.figure(figsize=(10,6))
annual_volatility.sort_values().plot(kind='bar')
plt.title('Annualized Volatility')
plt.ylabel('Volatility')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
volatility_filename = os.path.join(general_charts_folder, 'annualized_volatility_bar_chart.png')
plt.savefig(volatility_filename, dpi=300, bbox_inches='tight')
print(f"Annualized volatility chart saved as '{volatility_filename}'.")
plt.close()

# Correlation matrix
corr = log_returns.corr()

plt.figure(figsize=(10,8))
sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, fmt=".2f")
plt.title('Correlation Matrix of Log Returns')
plt.savefig(os.path.join(general_charts_folder, 'correlation_matrix_heatmap.png'), dpi=300, bbox_inches='tight')
print(f"Correlation matrix chart saved as '{os.path.join(general_charts_folder, 'correlation_matrix_heatmap.png')}'.")
plt.close()

print("\nAnalysis complete. All charts saved to respective folders.")