import requests
import time
import hashlib
import hmac
import uuid
import logging

API_KEY = 'YOUR_API_KEY'
SECRET_KEY = 'YOUR_SECRET_KEY'
URL = "https://api.bybit.com"
RECV_WINDOW = str(5000)

# Initialize HTTP client session
httpClient = requests.Session()

# Configure logging
logging.basicConfig(filename='trading.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

def http_request(end_point, method, payload, info):
    """Make an authenticated HTTP request."""
    timestamp = str(int(time.time() * 1000))
    signature = generate_signature(payload, timestamp)

    headers = {
        'X-BAPI-API-KEY': API_KEY,
        'X-BAPI-SIGN': signature,
        'X-BAPI-SIGN-TYPE': '2',
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': RECV_WINDOW,
        'Content-Type': 'application/json'
    }

    url = URL + end_point

    try:
        if method == "POST":
            response = httpClient.request(method, url, headers=headers, data=payload)
        else:
            response = httpClient.request(method, url + "?" + payload, headers=headers)

        logging.info(f"Order Details: {response.text}")
        logging.info(f"{info} Elapsed Time: {response.elapsed}")
    
    except Exception as e:
        logging.error(f"Error occurred during HTTP request: {e}")

def generate_signature(payload, timestamp):
    """Generate HMAC signature for the request."""
    param_str = timestamp + API_KEY + RECV_WINDOW + payload
    hash = hmac.new(bytes(SECRET_KEY, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
    return hash.hexdigest()

def create_order(qty, symbol, side, stop_loss=None, take_profit=None):
    """Create a market order with optional stop loss and take profit."""
    symbol = ''.join(symbol.split('/'))
    order_link_id = uuid.uuid4().hex

    data = {
        "symbol": symbol,
        "orderType": "Market",
        "side": side,
        "qty": str(qty),
        "price": "28000",  # Set your desired price here
        "timeInForce": "GoodTillCancel",
        "category": "inverse",
        "orderLinkId": order_link_id
    }

    if stop_loss:
        data["stopLoss"] = str(stop_loss)

    if take_profit:
        data["takeProfit"] = str(take_profit)

    endpoint = "/contract/v3/private/order/create"
    method = "POST"
    payload = json.dumps(data)

    http_request(endpoint, method, payload, f"Create {side} order")

def set_leverage(leverage, symbol):
    """Set leverage for a specific symbol."""
    symbol = ''.join(symbol.split('/'))
    data = {
        "symbol": symbol,
        "buyLeverage": str(leverage),
        "sellLeverage": str(leverage)
    }

    endpoint = "/contract/v3/private/position/set-leverage"
    method = "POST"
    payload = json.dumps(data)

    http_request(endpoint, method, payload, "Set Leverage")

# Example usage:
if __name__ == "__main__":
    # Create a buy market order with stop loss
    create_order(qty=10, symbol="BTC/USDT", side="Buy", stop_loss=27000)

    # Set leverage for a symbol
    set_leverage(leverage=10, symbol="BTC/USDT")
