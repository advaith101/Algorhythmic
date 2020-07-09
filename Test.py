import ccxt
import datetime
import time
import random
from pprint import pprint

def run():
    binance = ccxt.binance({
        'apiKey': 'nF5CYuh83iNzBfZyqOcyMrSg5l0wFzg5FcAqYhuEhzAbikNpCLSjHwSGXjtYgYWo',
        'secret': 'GaQUTvEurFvYAdFrkFNoHB9jiVyHX9gpaYOnIXPK0C3dugUKr6NHfgpzQ0ZyMfHx',
        'enableRateLimit': True,
        'timeout': 30000
    })
    print(binance)
    ticker = binance.fetch_ticker(symbol='ETH/BTC')
    average = (ticker['high'] + ticker['low']) / 2
    print(average)
    if binance.has['fetchOrders']:
       binance.load_markets()
       depth = binance.fetch_order_book(symbol='ETH/BTC')
       print(" ASK:", depth['asks'][0], depth['asks'][len(depth['asks']) - 1])
       print(" BID:", depth['bids'][0], depth['bids'][len(depth['bids']) - 1])
       lowestAsk = depth['asks'][0][0]
       highestAsk = depth['asks'][len(depth['asks']) - 1][0]
       highestBid = depth['bids'][0][0]
       lowestBid = depth['bids'][len(depth['bids']) - 1][0]
       print("Current Diff:", highestBid - lowestAsk)
       print("Possible Diff:", highestBid, lowestBid, highestAsk, lowestAsk)
       checkForOpenOrder(ccxt.binance(), 'ETH/BTC')

def checkForOpenOrder(exchange, market):
    isOpenOrder = True
    check = exchange.fetchOpenOrders(symbol= market)
    while isOpenOrder:
        if (len(check) == 0):
            isOpenOrder = False
        time.sleep(1)
        check = exchange.fetchOpenOrders(symbol= market)
        print(check)
    print("Order is Complete")

run()
