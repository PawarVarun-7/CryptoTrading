import ccxt
import time
import numpy as np
import Trade1 as Trade1  # Assuming Trade1 module contains necessary trade functions
import talib as ta

# Global variables for trade details
symbol = ""
ema5_length = 0
ema20_length = 0
ema30_length = 0
rsi_length = 0
stop_loss = 0
timeframe = ""
flag = 0
MACD_fastlength = 0
MACD_slowlength = 0
SIGNAL_signal_line = 0
rsi_oversold = 0

# Initialize the exchange (Bybit in this case)
exchange = ccxt.bybit({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET_KEY',
    'enableRateLimit': True
})

def get_trade_details():
    """Prompt user for trade details and start trading."""
    global symbol, ema5_length, ema20_length, ema30_length, rsi_length, stop_loss, timeframe, flag, MACD_fastlength, MACD_slowlength, SIGNAL_signal_line, rsi_oversold

    symbol = input("Symbol: ")
    ema5_length = int(input("EMA5 Length: "))
    ema20_length = int(input("EMA20 Length: "))
    ema30_length = int(input("EMA30 Length: "))
    MACD_fastlength = int(input("MACD Fast Length: "))
    MACD_slowlength = int(input("MACD Slow Length: "))
    SIGNAL_signal_line = int(input("MACD Signal Line: "))
    rsi_length = int(input("RSI Length: "))
    rsi_oversold = int(input("RSI Oversold Level: "))
    flag = float(input("Use Stop Loss? (0 for Yes, 1 for No): "))

    if flag == 0:
        stop_loss = float(input("Stop Loss Percentage: "))
        if stop_loss == 0:
            print("Invalid input. Stop loss percentage cannot be 0.")
            exit()

    timeframe = input("Timeframe: ")

    # Calculate the quantity based on available balance and percentage
    percentage = get_percentage_input()
    available_balance = exchange.fetch_balance()['USDT']['free']
    qty1 = calculate_quantity(percentage, available_balance, symbol)

    q = int(input("Data Fetch Rate (seconds): "))
    start(q, qty1)

def get_percentage_input():
    """Prompt user for percentage input with validation."""
    while True:
        try:
            percentage = float(input("Enter the percentage of available balance to use for trading (e.g. 50): "))
            if 0 < percentage <= 100:
                return percentage
            else:
                print("Percentage must be between 0 and 100. Please try again.")
        except ValueError:
            print("Invalid percentage. Please enter a valid number.")

def calculate_quantity(percentage, available_balance, symbol):
    """Calculate the quantity based on the percentage of available balance."""
    ticker = exchange.fetch_ticker(symbol)
    price = ticker['last']
    leverage = get_leverage_input()

    qty = (leverage * ((available_balance * percentage) / 100)) / price
    return round(qty, 3)

def get_leverage_input():
    """Prompt user for leverage input with validation."""
    while True:
        try:
            leverage = float(input("Enter the leverage to use for trading (e.g. 10): "))
            if leverage > 0:
                return leverage
            else:
                print("Leverage must be greater than 0. Please try again.")
        except ValueError:
            print("Invalid leverage. Please enter a valid number.")

def start(data_fetch_rate, quantity):
    """Start the trading loop with specified data fetch rate and quantity."""
    global c, b, f
    c = 0
    b = 0
    f = 0

    while True:
        # Fetch OHLCV data
        ohlcv = fetch_ohlcv_data(symbol, timeframe, limit=200 + ema20_length)
        close = np.array([ohlcv[i][4] for i in range(len(ohlcv))])

        # Calculate technical indicators
        ema5 = ta.EMA(close, timeperiod=ema5_length)
        ema20 = ta.EMA(close, timeperiod=ema20_length)
        ema30 = ta.EMA(close, timeperiod=ema30_length)
        rsi = ta.RSI(close, timeperiod=rsi_length)
        macd, signal, hist = ta.MACD(close, fastperiod=MACD_fastlength, slowperiod=MACD_slowlength, signalperiod=SIGNAL_signal_line)

        # Check trading conditions
        long_condition = (ema5[-1] > ema20[-1] > ema30[-1]) and (rsi[-1] > rsi_oversold) and (hist[-1] > 0)
        short_condition = (ema5[-1] < ema20[-1] < ema30[-1]) and (rsi[-1] < rsi_oversold) and (hist[-1] < 0)

        execute_trades(long_condition, short_condition, quantity)

        time.sleep(data_fetch_rate)

def fetch_ohlcv_data(symbol, timeframe, limit):
    """Fetch OHLCV data from the exchange."""
    return exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

def execute_trades(long_condition, short_condition, quantity):
    """Execute trades based on trading conditions."""
    global c, b, f
    if long_condition and (c == 0 and f == 0):
        print("Long order placed.")
        place_order(quantity, 'buy')
        c = 1
        f = 1
    elif short_condition and (b == 0 and f == 0):
        print("Short order placed.")
        place_order(quantity, 'sell')
        b = 1
        f = 1
    elif (not long_condition and c == 1) or (not short_condition and b == 1):
        print("Position closed.")
        place_order(quantity, 'sell' if c == 1 else 'buy')
        c = 0
        b = 0
        f = 0

def place_order(quantity, order_type):
    """Place buy or sell order."""
    if flag == 0:
        stop_loss_price = calculate_stop_loss_price(order_type)
        Trade1.place_stop_loss_order(stop_loss_price, quantity, symbol, order_type)
        print(f"{order_type.capitalize()} stop loss placed.")
    else:
        Trade1.place_market_order(quantity, symbol, order_type)
        print(f"{order_type.capitalize()} order placed.")

def calculate_stop_loss_price(order_type):
    """Calculate stop loss price based on order type."""
    close_price = exchange.fetch_ticker(symbol)['last']
    if order_type == 'buy':
        return close_price * (1 - (stop_loss / 100))
    else:
        return close_price * (1 + (stop_loss / 100))

if __name__ == "__main__":
    get_trade_details()
