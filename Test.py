import ccxt
import datetime
import time
import random
from pprint import pprint
import asyncio

def run():
    binance = ccxt.binance({
        'apiKey': 'nF5CYuh83iNzBfZyqOcyMrSg5l0wFzg5FcAqYhuEhzAbikNpCLSjHwSGXjtYgYWo',
        'secret': 'GaQUTvEurFvYAdFrkFNoHB9jiVyHX9gpaYOnIXPK0C3dugUKr6NHfgpzQ0ZyMfHx',
        'enableRateLimit': True,
        'timeout': 30000
    })
    print(binance)
    ticker = exchange.fetch_ticker(symbol=market)
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
    if binance.has['fetchOpenOrders']:
       depth = binance.fetchOpenOrders('ETH/BTC')
       print("Open Order Book: ", depth)
    if binance.has['fetchClosedOrders']:
       depth = binance.fetch_closed_orders(symbol='ETH/BTC')
       print("Closed Order Book: ", depth)

run()
