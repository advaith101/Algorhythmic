import ccxtpro
import ccxt
import datetime
import time
import random
from pprint import pprint
import asyncio
import requests
import json
import pandas as pd
import numpy as np
import decimal

transfer_symbol = 'USDC'
amount_digits_rounded = 5
percentUncertaintyOverAverage = .3
fee_pcts = {
    'binanceus': .001,
    'kraken': .0026,
    'bittrex': .005
}

async def run():
    usd_markets = await config_arbitrages()
    while 1:
        await scalp(usd_markets)
        # await compute_avg_spread(profit_spread_list, profit_dollars_list, quantity_list)
        print("\n\n---------------CYCLE FINISHED---------------\n\n")
        #For now we can choose to continue with next cycle
        x = input("Do you want to start next cycle? (y/n)")
        while x != 'n':
            if x == 'y':
                break
            x = input("Invalid Input: Do you want to start next cycle? (y/n)")
        if x == 'n':
            break
        continue
        print("CYCLE FINISHED, STARTING NEXT CYCLE...")
        # await asyncio.sleep(3)
    print("\n\nEsra CryptoBot has finished running\n\n")


async def config_arbitrages():
    print("\n\n ----------------------------------- \n\n")
    print("\n\nEsra Crypto Scalper Running....\n\n")
    print("Copyright 2020 Esra Systems All Rights Reserved visit www.esrainvestments.com for more info\n\n")
    print("\n\n ----------------------------------- \n\n")
    time.sleep(2)
    usd_markets = {}
    for exch in ccxtpro.exchanges:  # initialize Exchange
        # filtered_exchanges = [ 'binance', 'coinbase' 'bequant', 'binanceje', 'binanceus', 'bitfinex', 'bitmex', 'bitstamp', 'bittrex', 'bitvavo', 'coinbaseprime', 'coinbasepro', 'ftx', 'gateio', 'hitbtc', 'huobijp',
        #                         'huobipro', 'huobiru', 'kraken', 'kucoin', 'okcoin', 'okex', 'phemex', 'poloniex', 'upbit']
        filtered_exchanges = ['binanceus']
        if exch not in filtered_exchanges:
            continue
        if exch == 'binanceus':
            exchange1 = getattr(ccxtpro, 'binanceus')({
                'apiKey': 'W6fJUrx0LLcrdNE1GJ9B5yK0NRPMhhWjDtotxrdI3FirqUlBIzNHtWdza0TLn2Sy',
                'secret': 'TIAIQHixpiIeUOXRaf3joBVJP9rHizsEcALDuadL1VAeZCsPMem3KtxRfWMYZth9',
                'timeout': 30000,
                'enableRateLimit': True
                })
        elif exch == 'coinbase':
            exchange1 = getattr(ccxtpro, 'coinbase')({
                'apiKey': '4pUQ6RrdifyAObzH',
                'secret': 'vJcrS1EOhlmiP4jdvTR11NWljeXM0RDr',
                'timeout': 30000,
                'enableRateLimit': True
                })
        elif exch == 'kraken':
            exchange1 = getattr(ccxtpro, 'kraken')({
                'apiKey': '23c833b7f0474c26b6367081904b9083',
                'secret': 'f8cd636f627d4680b28a01af8b48cfca',
                'timeout': 30000,
                'enableRateLimit': True
                })
        else:
            exchange1 = getattr(ccxtpro, exch)()
        try:
            val = await exchange1.load_markets()
            markets = val.keys()
        except:
            print('\nExchange is not loading markets.. Moving on\n')
            continue
        print("Exchange Name: {}".format(exchange1.id))
        usd_markets_in_exchange = []
        for symb in exchange1.symbols:
            if symb.split('/')[1] in ['USD', 'USDC', 'USDT', 'BUSD']:
                usd_markets_in_exchange.append(symb)
        usd_markets[exchange1.id] = usd_markets_in_exchange
        exchange1.close()
    return usd_markets


#Executes scalping strategy where we look for when the 15 EMA intersects and crosses the 75 EMA and buy/sell depending on direction
async def scalp(usd_markets):
    for exch in usd_markets:
        if exch == 'binanceus':
            exchange1 = getattr(ccxtpro, 'binanceus')({
                'apiKey': 'W6fJUrx0LLcrdNE1GJ9B5yK0NRPMhhWjDtotxrdI3FirqUlBIzNHtWdza0TLn2Sy',
                'secret': 'TIAIQHixpiIeUOXRaf3joBVJP9rHizsEcALDuadL1VAeZCsPMem3KtxRfWMYZth9',
                'timeout': 30000,
                'enableRateLimit': True
                })
        elif exch == 'coinbase':
            exchange1 = getattr(ccxtpro, 'coinbase')({
                'apiKey': '4pUQ6RrdifyAObzH',
                'secret': 'vJcrS1EOhlmiP4jdvTR11NWljeXM0RDr',
                'timeout': 30000,
                'enableRateLimit': True
                })
        elif exch == 'kraken':
            exchange1 = getattr(ccxtpro, 'kraken')({
                'apiKey': '23c833b7f0474c26b6367081904b9083',
                'secret': 'f8cd636f627d4680b28a01af8b48cfca',
                'timeout': 30000,
                'enableRateLimit': True
                })
        else:
            exchange1 = getattr(ccxtpro, exch)()
        try:
            await exchange1.load_markets()
        except:
            print('\nExchange is not loading markets.. Moving on\n')
            continue
        for market in usd_markets[exch]:
            thirty_min_candles = await exchange1.fetch_ohlcv(market, '30m')
            # print("SYMBOL: {} \n\n".format(market))
            # print(thirty_min_candles)
            hour_candles = await exchange1.fetch_ohlcv(market, '1h')
            fourhour_candles = await exchange1.fetch_ohlcv(market, '4h')
            thirty_min_ema_15 = await calc_emas(thirty_min_candles, 15)
            print("SYMBOL: {} \n\n".format(market))
            thirty_min_bollingers_20 = await calc_bollingers(thirty_min_candles, 20)





#Below are strategies that trade based on one indicator alone


#Double ema strategy - check ema 75 (4h) for general trend, if bullish or bearish, add 3 to buy or sell signal respectively.
#Then, proceed to finding most recent candle where EMA 15 intersected (or got within 2 pips of) EMA 75, if too long ago continue, else, 
# check for "power move" or when the candle of intersection has a high spread between open and close price, if there is a power move, 
#buy/sell in the direction of the move. Else, wait for a little for a power move to start (honestly prolly wait for next cycle).
async def double_ema(market, exchange):
    buy_signal = 0
    sell_signal = 0
    general_trend = ''
    intersect_candle =[]

    #find general trend
    candles = await exchange.fetch_ohlcv(market, '1h')
    emas_long = await calc_emas(candles, 75)
    x_vals = np.arange(0,len(emas))
    y_vals = np.array(emas)
    first_deg_poly = np.polyfit(x_vals, y_vals, 1)
    second_deg_poly = np.polyfit(x_vals, y_vals, 2)
    if first_deg_poly[0] > 0.1:
        if second_deg_poly[0] > .2:
            general_trend = 'strong bullish'
            buy_signal += 2
        else:
            general_trend = 'bullish'
            buy_signal += 1
    elif first_deg_poly[0] < -0.1:
        if second_deg_poly[0] < -.2:
            general_trend = 'strong bearish'
            sell_signal += 2
        else:
            general_trend = 'bearish'
            sell_signal += 1
    else:
        general_trend = 'neutral'

    #find candle of most recent intersection
    emas_short = (await calc_emas(candles, 5))[-1:0:-1]
    emas_medium = (await calc_emas(candles, 15))[-1:0:-1]
    i = 0
    direction = ""
    for a in range(len(emas_medium)):
        if emas_short[a + 10] < emas_medium[a]:
            if i == 1:
                direction = "Crossed Bearish"
                intersect_candle = (candles[-1:0:-1])[a + 15]
                buy_signal += 4
            i = -1
        elif emas_short[a + 10] > emas_medium[a]:
            if i == -1:
                direction = "Crossed Bullish"
                intersect_candle = (candles[-1:0:-1])[a + 15]
                sell_signal += 4
            i = 1
        else:
            intersect_candle = (candles[-1:0:-1])[a + 15]
            if i == -1:
                direction = "Crossed Bearish"
                buy_signal += 4
            elif i == 1:
                direction = "Crossed Bullish"
                sell_signal += 4

    #checks volume of intersection candle to see if "power move" is present
    if len(intersect_candle) == 0:
        print("No double EMA intersection found recently")
        return None
    candle_vol = intersect_candle[1] - intersect_candle[4]
    if (candle_vol/intersect_candle[1]) * 100 > 1:
        if direction == "Crossed Bullish":
            buy_signal += 4
        elif direction == "Crossed Bearish":
            sell_signal += 4
    return {
        'buy_signal': buy_signal,
        'sell_signal': sell_signal
    }
    










#Below are indicators that we will be using in our strategies#


#Calculates EMA's for each set of candles (ie if you plot it it would be the EMA)
async def calc_emas(candles, length):
    emas = []
    i = 0
    num_first = 0
    sum_first = 0
    first_after_period = True
    prev_ema = 0
    for candle in candles[-1:0:-1]:
        if i <= length:
            sum_first += candle[4]
            num_first += 1
            i += 1
            continue
        if first_after_period:
            sma = sum_first/num_first
            ema = await calc_ema(length, candle[4], sma)
            prev_ema = ema
            emas.append(ema)
            first_after_period = False
        else:
            ema = await calc_ema(length, candle[4], prev_ema)
            emas.append(ema)
            prev_ema = ema
    #print(emas)
    return emas
    

#calculates ema for a particular candle
async def calc_ema(length, curr_price, prev_ema):
    weight_factor = 2/(length + 1)
    ema = weight_factor * (curr_price - prev_ema) + prev_ema
    return ema


#Calculates Bollinger Bands given candlesticks
async def calc_bollingers(candles, length):
    bollingers = []
    i = 0
    length_candles = []
    sma = 0
    for candle in candles:
        if i < length:
            length_candles.append(candle)
            i += 1
            continue
        length_candles.append(candle)
        close_prices = []
        for cand in length_candles:
            close_prices.append(cand[4])
        # print("\nCLOSE PRICES:{}".format(close_prices))
        sma = np.average(close_prices)
        bollinger = await calc_bollinger(close_prices, sma)
        # print(bollinger)
        bollingers.append(bollinger)
        length_candles.pop(0)
        # print(length_candles)
        i += 1
    print(bollingers)
    return bollingers


#helper method that calculates bollinger values for particular candle
async def calc_bollinger(close_prices, sma):
    stdev = np.std(close_prices)
    # print("\n\nSTD: {}".format(stdev))
    return [sma + 2*stdev, sma, sma - 2*stdev]








asyncio.get_event_loop().run_until_complete(run())

if __name__ == "__main__":
    run()