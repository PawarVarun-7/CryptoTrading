import ccxt
import talib as ta
import requests
import pandas as pd
import numpy as np
# Create an exchange instance
exchange = ccxt.bybit({
    'apiKey': '',
    'secret': '',
    'enableRateLimit': True
})

# Set symbol and timeframe
symbol = 'SOL/USDT'
timeframe = '15m'
ema5_length = 5
ema20_length = 20
rsi_length = 14
rsi_oversold = 49
# Fetch historical candle data
exchange = 'bybit'
pair = 'solusdt'

# Define the API endpoint URL
url = f'https://api.cryptowat.ch/markets/{exchange}/{pair}/ohlc'

# Define the parameters for the API request
params = {
    # candlestick interval, in seconds (86400 seconds = 1 day)
    'periods': '3600',
    # timestamp of the first candlestick
    'after': int(pd.Timestamp.now(tz='UTC').timestamp() - 42 * 86400),
}

# Send the API request and fetch the response data
response = requests.get(url, params=params)
data = response.json()

# Convert the response data to a pandas DataFrame
df1 = pd.DataFrame(data['result'][str(params['periods'])], columns=[
                   'timestamp', 'open', 'high', 'low', 'close', 'volume', 'NA'])

ha_close = (np.array(df1['open']) + np.array(df1['high']) +
            np.array(df1['low']) + np.array(df1['close'])) / 4
ha_open = np.zeros_like(ha_close)
ha_high = np.zeros_like(ha_close)
ha_low = np.zeros_like(ha_close)
for i in range(1, len(df1)):
    ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2
    ha_high[i] = np.array([df1['high'].iloc[i], ha_open[i], ha_close[i]]).max()
    ha_low[i] = np.array([df1['low'].iloc[i], ha_open[i], ha_close[i]]).min()
# Fetch OHLCV data for the past 4000 candles
# ohlcv = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=4000)

# df1 = pd.DataFrame(
#     ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
# print(df1)
# ha_close = (np.array(ohlcv)[:, 1] + np.array(ohlcv)[:, 2] +
#             np.array(ohlcv)[:, 3] + np.array(ohlcv)[:, 4]) / 4
# ha_open = np.zeros_like(ha_close)
# ha_high = np.zeros_like(ha_close)
# ha_low = np.zeros_like(ha_close)
# for i in range(1, len(ohlcv)):
#     ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2
#     ha_high[i] = np.array([ohlcv[i][2], ha_open[i], ha_close[i]]).max()
#     ha_low[i] = np.array([ohlcv[i][3], ha_open[i], ha_close[i]]).min()

# Create a pandas dataframe from the Heikin Ashi candles data
df = pd.DataFrame({
    'timestamp': df1['timestamp'],
    'open': ha_open,
    'high': ha_high,
    'low': ha_low,
    'close': ha_close,
})
print(df)
# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Set timestamp as index
df.set_index('timestamp', inplace=True)

# Calculate the EMA5 and EMA20
df['EMA5'] = ta.EMA(df['close'], timeperiod=ema5_length)
df['EMA20'] = ta.EMA(df['close'], timeperiod=ema20_length)

# Calculate the RSI
df['RSI'] = ta.RSI(df['close'], timeperiod=rsi_length)

# Initialize variables
trades = []
winning_trades = []
losing_trades = []
total_profit = 0
gross_profit = 0
gross_loss = 0
trading_fee = 0.007/100
buysell = []
sq1 = []
sq2 = []
global f1, f2
f1 = 0
f2 = 0
z = 0
# Loop through each row of the DataFrame
for i, row in df.iterrows():
    close_price = row['close']
    open_price = row['open']
    ema5 = row['EMA5']
    ema20 = row['EMA20']
    rsi = row['RSI']

    # Entry long
    if ema5 > ema20 and rsi > rsi_oversold and f1 == 0:
        trades.append(('buy', open_price))
        buysell.append('long buy')
        sq1.append(1)
        f1 = 1
        z = z+1
        if z == 1:
            Starting = open_price
    # Entry short
    elif ema5 < ema20 and rsi < rsi_oversold and f2 == 0:
        trades.append(('sell', open_price))
        buysell.append('short sell')
        sq2.append(1)
        f2 = 1
        z = z+1
        if z == 1:
            Starting = open_price
    elif (close_price < ema20 or rsi < rsi_oversold) and f1 == 1:

        entry_price = trades[-1][1]
        profit = close_price - entry_price
        total_profit += profit
        f1 = 0
        buysell.append('long sell')
        sq1.append(0)
        if profit > 0:
            winning_trades.append(profit)
            gross_profit += profit
        else:
            losing_trades.append(profit)
            gross_loss += abs(profit)

        trades.pop()

    # Exit short
    elif (close_price > ema20 or rsi > rsi_oversold) and f2 == 1:
        entry_price = trades[-1][1]
        profit = entry_price - close_price
        total_profit += profit
        f2 = 0
        buysell.append('short buy')
        sq2.append(0)
        if profit > 0:
            winning_trades.append(profit)
            gross_profit += profit
        else:
            losing_trades.append(profit)
            gross_loss += abs(profit)

        trades.pop()
global a, b, c, d
a = 0
b = 0
c = 0
d = 0
for i in range(len(sq1)):
    if sq1[i] == 1:

        a = a+1
    if sq1[i] == 0:

        b = b+1
if a == b:
    print("Squared Long buysell")
print(f"a :{a} , b :{b} ")
for i in range(len(sq2)):
    if sq2[i] == 1:

        c = c+1
    if sq2[i] == 0:

        d = d+1
if c == d:
    print("Squared short buysell")
print(f"c :{c} , d :{d} ")
print("--------------------------------------------------------------")
print(trades)
# Calculate statistics
num_winning_trades = len(winning_trades)
num_losing_trades = len(losing_trades)
profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
average_winning_trade = sum(
    winning_trades) / num_winning_trades if num_winning_trades > 0 else 0
net_profit = total_profit - \
    (num_winning_trades * 2 * trading_fee) - \
    (num_losing_trades * 2 * trading_fee)

# Print results
print(f"total profit: {total_profit} USD")
print(f"Initial capital: {Starting} USD")
print(f"Gross profit: {gross_profit:.2f} USD")
print(f"Gross loss: {gross_loss:.2f} USD")
print(f"Net profit: {net_profit:.2f} USD")
print(f"Profit factor: {profit_factor:.2f}")
print(f"Average winning trade: {average_winning_trade:.2f}")
