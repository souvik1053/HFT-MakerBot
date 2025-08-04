import time
from binance.client import Client
from binance.exceptions import BinanceAPIException
from config import API_KEY, API_SECRET

SYMBOL = 'BTCUSDT'
SPREAD = 0.001  # 0.1%
QTY = 0.001     # order size
MAX_POSITION = 0.002  # max long or short

client = Client(API_KEY, API_SECRET)
client.API_URL = 'https://testnet.binance.vision/api'

def get_mid_price():
    book = client.get_orderbook_ticker(symbol=SYMBOL)
    bid = float(book['bidPrice'])
    ask = float(book['askPrice'])
    return bid, ask, (bid + ask) / 2

def cancel_open_orders():
    try:
        orders = client.get_open_orders(symbol=SYMBOL)
        for o in orders:
            client.cancel_order(symbol=SYMBOL, orderId=o['orderId'])
    except BinanceAPIException as e:
        print("Cancel error:", e)

def get_position():
    try:
        trades = client.get_my_trades(symbol=SYMBOL)
        pos = 0.0
        for t in trades:
            qty = float(t['qty'])
            if t['isBuyer']:
                pos += qty
            else:
                pos -= qty
        return pos
    except BinanceAPIException as e:
        print("Trade fetch error:", e)
        return 0.0


def quote():
    bid, ask, mid = get_mid_price()
    bid_px = round(mid * (1 - SPREAD), 2)
    ask_px = round(mid * (1 + SPREAD), 2)
    pos = get_position()

    cancel_open_orders()

    if pos < MAX_POSITION:
        print(f"Placing BUY @ {bid_px}")
        client.create_test_order(symbol=SYMBOL, side='BUY', type='LIMIT',
                                 timeInForce='GTC', quantity=QTY, price=str(bid_px))
    if pos > -MAX_POSITION:
        print(f"Placing SELL @ {ask_px}")
        client.create_test_order(symbol=SYMBOL, side='SELL', type='LIMIT',
                                 timeInForce='GTC', quantity=QTY, price=str(ask_px))
    print(f"Position = {pos:.6f}")

def run():
    while True:
        try:
            quote()
        except Exception as e:
            print("Error:", e)
        time.sleep(1)

if __name__ == '__main__':
    run()
    
    
