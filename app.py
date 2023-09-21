import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Define a function to fetch and concatenate the closing prices of multiple cryptocurrencies
def fetch_and_concat_closing_prices(*crypto_symbols):
    """
    Fetch and concatenate the closing prices of multiple cryptocurrencies.
    
    Args:
        *crypto_symbols (str): Variable number of cryptocurrency symbols.
        
    Returns:
        pd.DataFrame: A DataFrame containing the concatenated closing prices.
    """
   # Initialize an empty DataFrame to store the closing prices
    all_closing_prices = pd.DataFrame()
    
    # Fetch data for each cryptocurrency symbol
    for symbol in crypto_symbols:
        # Fetch historical price data for the cryptocurrency within the selected date range
        crypto_data = yf.download(symbol, start=start_date, end=end_date, interval="1d", auto_adjust=True)
        
        # Extract the closing prices and rename the column
        closing_prices = crypto_data['Close'].rename(symbol)
        
        # Concatenate the closing prices to the DataFrame
        all_closing_prices = pd.concat([all_closing_prices, closing_prices], axis=1)
    
    return all_closing_prices
# Create a Streamlit app
st.title('Cryptocurrency Analysis')

# Create a widget to input cryptocurrency symbols
crypto_symbols = st.multiselect(
    'Select cryptocurrencies to include in the analysis',
    ['BTC-USD', 'ETH-USD', 'XRP-USD', 'LTC-USD', 'ADA-USD', 'BNB-USD', 'DOT-USD', 'LINK-USD', 'XLM-USD', 'SOL-USD', 'DOGE-USD', 'ETC-USD'],
    default=['BTC-USD', 'ETH-USD', 'XRP-USD', 'LTC-USD', 'ADA-USD', 'BNB-USD', 'DOT-USD', 'LINK-USD', 'XLM-USD', 'SOL-USD', 'DOGE-USD', 'ETC-USD']
)

# Create date input widgets for start and end dates
start_date = st.date_input('Select Start Date', pd.to_datetime('2022-01-01'))
end_date = st.date_input('Select End Date', pd.to_datetime('2023-01-01'))

if not crypto_symbols:
    st.warning('Please select at least one cryptocurrency.')

else:
    # Fetch and concatenate the closing prices of the selected cryptocurrencies
    crypto_closing_prices = fetch_and_concat_closing_prices(*crypto_symbols)

    # Calculate the daily returns for each cryptocurrency
    crypto_returns = crypto_closing_prices.pct_change().dropna()

    # Create a heatmap
    st.write('Cryptocurrency Correlation Heatmap')
    plt.figure(figsize=(10, 6))
    sns.heatmap(crypto_returns.corr(), annot=True, cmap='coolwarm', linewidths=0.5)
    st.pyplot(plt)

# Section for more information or analysis
st.subheader('Additional Analysis')

# Display summary statistics of the selected cryptocurrencies
st.write("Summary Statistics of Selected Cryptocurrencies:")
st.write(crypto_closing_prices.describe())

# Display the top correlated pairs
st.subheader('Top Correlated Cryptocurrency Pairs (Excluding Self-Correlations):')

# Calculate the correlation matrix
correlation_matrix = crypto_returns.corr()

# Initialize an empty list to store the top correlated pairs
top_correlations = []

# Iterate through the correlation matrix and find the top correlated pairs
for symbol1 in crypto_symbols:
    for symbol2 in crypto_symbols:
        if symbol1 != symbol2:
            correlation = correlation_matrix.loc[symbol1, symbol2]
            top_correlations.append((symbol1, symbol2, correlation))

# Sort the top_correlations list by correlation (highest to lowest)
top_correlations.sort(key=lambda x: x[2], reverse=True)

# Create a DataFrame from the top_correlations list
top_correlations_df = pd.DataFrame(top_correlations, columns=['Cryptocurrency 1', 'Cryptocurrency 2', 'Correlation'])

# Drop duplicate pairs based on correlation value
top_correlations_df.drop_duplicates(subset=['Cryptocurrency 1', 'Cryptocurrency 2'], inplace=True)

# Display the unique top correlated pairs in a DataFrame
st.write(top_correlations_df)

# Additional Analysis Section 1: Price Line Charts
st.subheader('Price Line Charts')
st.write('Historical price movements for selected cryptocurrencies:')
st.line_chart(crypto_closing_prices)

# Additional Analysis Section 3: Volume Analysis
st.subheader('Volume Analysis')
st.write('Trading volume trends for selected cryptocurrencies:')
st.line_chart(yf.download(crypto_symbols, interval="1d", auto_adjust=True)['Volume'])

# Additional Analysis Section 4: Moving Averages (50-day and 200-day)
st.subheader('Moving Averages')
st.write('50-day and 200-day moving averages for selected cryptocurrencies:')

# Calculate the 50-day and 200-day moving averages for each cryptocurrency individually
moving_averages_50 = crypto_closing_prices.rolling(window=50).mean()
moving_averages_200 = crypto_closing_prices.rolling(window=200).mean()

# Create separate line charts for each moving average
for symbol in crypto_symbols:
    st.write(f'{symbol} Moving Averages')
    plt.figure(figsize=(10, 6))
    plt.plot(moving_averages_50[symbol], label='50-day MA', alpha=0.7)
    plt.plot(moving_averages_200[symbol], label='200-day MA', alpha=0.7)
    plt.legend()
    st.pyplot(plt)


# Additional Analysis Section 6: Performance Metrics
st.subheader('Performance Metrics')
st.write('Performance metrics for selected cryptocurrencies:')
performance_metrics = crypto_closing_prices.apply(lambda col: col / col.iloc[0] - 1)
st.line_chart(performance_metrics)