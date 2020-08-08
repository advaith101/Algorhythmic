import ccxt
import time
import random
from pprint import pprint

#NOTES: Looking through the Bid Order Book, Ask Order Book, how can we find the best deal for a bid price or ask price? Or should the bid order or ask order be a market order placement?
def maxBid(exchange, market, min_USD_for_trade = 100): #make exchange, exch_rate_list, sym_list, fee_percentage global vars
    USDCmarket = market[0:3] + "/USDC"
    USDCdepth = exchange.fetch_order_book(symbol = USDCmarket) #checking the price of a coin in dollars
    try:
        min_quantity = round(float(min_USD_for_trade/(USDCdepth['bids'][0][0])), 5) #minimum quantity that will determine the correct bid price
        depth = exchange.fetch_order_book(symbol = market)
        for bid in depth['bids']:
            if bid[1] > min_quantity:
                return float(bid[0], 5)
        return 0
    except:
        return 0

def minAsk(exchange, market, min_USD_for_trade = 100):
    USDCmarket = market[0:3] + "/USDC"
    USDCdepth = exchange.fetch_order_book(symbol = USDCmarket) #checking the price of a coin in dollars
    try:
        min_quantity = round(float(min_USD_for_trade/(USDCdepth['asks'][0][0])), 5) #minimum quantity that will determine the correct bid price
        depth = exchange.fetch_order_book(symbol = market)
        for ask in depth['asks']:
            if ask[1] > min_quantity:
                return float(ask[0], 5)
        print("No Asks Found in Order Book")
        return 9999999999
    except:
        return 9999999999

#Testing
sym_list = ["BNB/BTC", "ETH/USDT", "BNB/USDT"]
exchange = ccxt.binance()
print(minAsk(exchange, sym_list[0]))
print(exchange.symbols)
