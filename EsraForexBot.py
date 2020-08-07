import ccxtpro
import ccxt
from datetime import datetime, timedelta
import time
import random
from pprint import pprint
import asyncio
import requests
import json
import pandas as pd
import numpy as np
import decimal
import matplotlib.pyplot as plt
from oandapyV20 import API
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.forexlabs as labs
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.transactions as transactions
from oandapyV20.contrib.requests import MarketOrderRequest
import trendln


#account info for live acct.
# accountID = "001-001-4630515-001"
# access_token = "1d8b241d70c8860beb0a0a8455e48e5f-3390fae9470905f3edf39b2b8c49e0df"

#account info for practice acct.
accountID = "101-001-16023947-001"
access_token = "9a5cae7cbfacf5f6aa634097bc1bc337-b394ef6856186107ebfdc589260269bf"

# oanda = API(environment="live", access_token=access_token)
oanda = API(access_token=access_token)
fee_pct = 0.0 # YESSIRRR OANDA IS FREE COMMISSION


async def run():
	#triarb strategy
	# tri_arbs = await config_arbitrages()
	# print("\n\n---------------TRIANGULAR ARBITRAGRE CONFIGURATION FINISHED---------------\n\n")
	# x = input("Now finding which arbs are profitable. Do you want to place actual orders? (y/n)")
	# order_mode = False
	# if x == 'y':
	# 	order_mode = True
	# count = 0
	# for arb in tri_arbs:
	# 	b = await execute_tri_arb(arb, order_mode, count)
	# 	if not b:
	# 		count += 1
	# print("\n-------------------------TRIANGULAR ARBITRATION FINISHED------------------------------\n")
	print("Starting master strategy... \n")
	await asyncio.sleep(3)
	scores_by_market = await scalp()


	# while 1:
	#     await execute_all_tri_arb_orders(tri_arbs)
	#     await execute_master_strategy()
	#     print("\n\n---------------CYCLE FINISHED---------------\n\n")
	#     #For now we can choose to continue with next cycle
	#     x = input("Do you want to start next cycle? (y/n)")
	#     while x != 'n':
	#         if x == 'y':
	#             break
	#         x = input("Invalid Input: Do you want to start next cycle? (y/n)")
	#     if x == 'n':
	#         break
	#     continue
	#     print("CYCLE FINISHED, STARTING NEXT CYCLE...")
	#     # await asyncio.sleep(3)
	# print("\n\nEsra CryptoBot has finished running\n\n")



###. TRI-ARB STUFF ###


async def config_arbitrages():
	instruments = oanda.request(accounts.AccountInstruments(accountID))["instruments"]
	symbols = [instrument['displayName'] for instrument in instruments]
	print("SYMBOLS:\n{}".format(json.dumps(symbols, indent=2)))
	list_of_arb_lists = []
	for symb in symbols:
		arb_list = [symb]
		j = 0
		while 1:
			if j >= 1:
				if len(arb_list) > 1:
					final = arb_list[0].split('/')[1] + '/' + str(arb_list[1].split('/')[1])
					if final in symbols:
						arb_list.append(final)
				break
			for sym in symbols:
				if sym in arb_list:
					continue
				if arb_list[0].split('/')[0] == sym.split('/')[0]:
					if arb_list[0] == sym:
						continue
					else:
						arb_list.append(sym)
						j += 1
						break
			j += 1
		if len(arb_list) > 2:
			if arb_list[2] in symbols:
				list_of_arb_lists.append(arb_list)

	print("\nList of Arbitrage Symbols:", list_of_arb_lists)
	return list_of_arb_lists


async def execute_tri_arb(arb_list, order_mode, count):
	profit, depth, prices = await find_profit(arb_list, fee_pct, 'market')
	if profit > 0.0:
		print("FOUND PROFITABLE ARBITRAGE \n")
		print("--------------------------- \n")
		print("Arbitrage Symbols: {}".format(arb_list))
		print("REAL PROFIT RATE: {}".format(profit))
		print("DEPTH: {} (This is forex, we dont even have to worry lol)".format(depth))
		# if order_mode:
		# 	#Create order here - needs to be finished
		# 	funds = await get_available_funds()
		# 	if count == 0:
		# 		order1, order2, order3 = await asyncio.ensure_future(create_triarb_order(arb_list, prices, funds))
		return True
			
	else:
		print("Not profitable :(")
		return False



async def create_triarb_order(arb_list, prices, available_funds):
	#funds = available_funds/2 #don't want to alot all our money to tri arb
	order1 = {
	  "order": {
	    "price": str(prices[0]),
	    "timeInForce": "GTC",
	    "instrument": arb_list[0].replace('/','_'),
	    "units": "20",
	    "type": "LIMIT",
	    "positionFill": "DEFAULT"
	  }
	}
	order2 = {
	  "order": {
	    "price": str(prices[1]),
	    "timeInForce": "GTC",
	    "instrument": arb_list[1].replace('/','_'),
	    "units": "-20",
	    "type": "LIMIT",
	    "positionFill": "DEFAULT"
	  }
	}
	order3 = {
	  "order": {
	    "price": str(prices[2]),
	    "timeInForce": "GTC",
	    "instrument": arb_list[2].replace('/','_'),
	    "units": str(20 * prices[1] * (1/prices[2])),
	    "type": "LIMIT",
	    "positionFill": "DEFAULT"
	  }
	}
	order1_task = oanda.request(orders.OrderCreate(accountID, data=order1))
	order2_task = oanda.request(orders.OrderCreate(accountID, data=order2))
	order3_task = oanda.request(orders.OrderCreate(accountID, data=order3))
	return order1_task, order2_task, order3_task

async def get_available_funds():
	available_funds = oanda.request(accounts.AccountDetails(accountID))['account']['NAV']
	print("NET ACCOUNT VALUE: {}".format(available_funds))
	return available_funds

async def find_profit(arb_list, fee_pct, strategy):
	spread = 0.0
	depth = 0.0
	prices = []
	params ={
		'instruments': '{},{},{}'.format(arb_list[0].replace('/','_'), arb_list[1].replace('/','_'), arb_list[2].replace('/','_'))
	}
	orderbook = oanda.request(pricing.PricingInfo(accountID=accountID, params=params))['prices']
	if strategy == 'limit':
		max_bid = orderbook[0]['bids'][0]
		min_ask = orderbook[1]['asks'][0]
		max_bid1 = orderbook[2]['bids'][0]
		spread = ((1/float(max_bid['price'])) * float(min_ask['price']) * (1/float(max_bid1['price']))) - 1
		depth = max_bid1['liquidity']
		prices = [float(max_bid['price']), float(min_ask['price']), float(max_bid1['price'])]
	elif strategy == 'market':
		min_ask = orderbook[0]['bids'][0]
		max_bid = orderbook[1]['asks'][0]
		min_ask1 = orderbook[2]['bids'][0]
		spread = ((1/float(min_ask['price'])) * float(max_bid['price']) * (1/float(min_ask1['price']))) - 1
		depth = min_ask1['liquidity']
		prices = [float(min_ask['price']), float(max_bid['price']), float(min_ask1['price'])]
	return spread, depth, prices

















### Master Strategy Stuff ###

#NEEDS TO BE DONE (place "DONE" next to it if complete):
#	1. add volatility indicator and refine double ema and rsi strategy
#	(DONE - NEEDS REFINING) 2. add support/resistance 
#	(DONE - NEEDS REFINING) 3. add MACD
#	4. add points of value strategy
#	5. get feedback - log P/L's and strategy scores for each position once it is closed. This will be used as a learner.
#	6. add Randomized Weighted Majority Algorithm to optimize weights for strategies over time

async def scalp(order_mode=False):
	instruments1 = oanda.request(accounts.AccountInstruments(accountID))["instruments"]
	symbols = [instrument['name'] for instrument in instruments1]
	symbols_display = [instrument['displayName'] for instrument in instruments1]
	scores_by_market = []
	i = 0
	for market in symbols:
		scores_by_market.append({
				'market': market,
				'strategy_scores': []
			})
		rsi_h1_score = await RSI_strategy(market, "H1")
		double_ema_score = await double_ema(market, "H1")
		MACD_score = await MACD_strategy(market, "H1")
		print("MARKET: {} \n".format(market))
		print("RSI score: {}".format(rsi_h1_score))
		print("double EMA score: {}".format(double_ema_score))
		print("MACD score: {}".format(MACD_score))
		scores_by_market[i]['strategy_scores'].extend([rsi_h1_score, double_ema_score, MACD_score])
		i += 1
	j = 0
	for marketscore in scores_by_market:
		overallscore = {}
		buy = 0
		sell = 0
		count = 0
		for strategyscore in marketscore['strategy_scores']:
			buy += strategyscore['buy_signal']
			sell += strategyscore['sell_signal']
			count += 1
		overallscore['buy_signal'] = buy/count
		overallscore['sell_signal'] = sell/count
		marketscore['overall_score'] = overallscore
		if (overallscore['buy_signal'] > 3.5 and overallscore['sell_signal'] < 2.5) or (overallscore['buy_signal'] < 2.5 and overallscore['sell_signal'] > 3.5):
			if order_mode:
				market_order = await asyncio.ensure_future(create_order(marketscore['market'], overallscore['buy_signal'], overallscore['sell_signal']))
	

	return scores_by_market



#Function to order based on overall score for 1 market
async def create_order(market, buy_signal, sell_signal):
	# if buy_signal > sell_signal:
	# 	mo = MarketOrderRequest(instrument=market, units=(buy_signal * 10000 - sell_signal * 10000))
	# 	market_order = oanda.request(orders.OrderCreate(accountID, data=mo.data))
	# elif sell_signal > buy_signal:
	# 	mo = MarketOrderRequest(instrument=market, units=(buy_signal * 10000 - sell_signal * 10000))
	mo = MarketOrderRequest(instrument=market, units=(buy_signal * 10000 - sell_signal * 10000))
	market_order = oanda.request(orders.OrderCreate(accountID, data=mo.data))
	#order confirmation
	print(json.dumps(market_order, indent=4))
	return market_order






#Below are strategies that trade based on one indicator alone


#Double ema strategy - check ema 75 (4h) for general trend, if bullish or bearish, add 3 to buy or sell signal respectively.
#Then, proceed to finding most recent candle where EMA 15 intersected (or got within 2 pips of) EMA 75, if too long ago continue, else, 
# check for "power move" or when the candle of intersection has a high spread between open and close price, if there is a power move, 
#buy/sell in the direction of the move. Else, wait for a little for a power move to start (honestly prolly wait for next cycle).
async def double_ema(market, length):
	buy_signal = 0
	sell_signal = 0
	general_trend = ''
	intersect_candle =[]

	#find general trend
	params = {
		"count": 500,
		"granularity": length
	}
	candles = oanda.request(instruments.InstrumentsCandles(instrument=market, params=params))['candles']
	emas_long = await calc_emas(candles, 75)
	x_vals = np.arange(0,len(emas_long))
	y_vals = np.array(emas_long)
	first_deg_poly = np.polyfit(x_vals, y_vals, 1)
	second_deg_poly = np.polyfit(x_vals, y_vals, 2)
	if first_deg_poly[0] > 0:
		if second_deg_poly[0] > .1:
			general_trend = 'strong bullish'
			buy_signal += 2
		else:
			general_trend = 'bullish'
			buy_signal += 1
	elif first_deg_poly[0] < 0:
		if second_deg_poly[0] < -.1:
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
				break
			i = -1
		elif emas_short[a + 10] > emas_medium[a]:
			if i == -1:
				direction = "Crossed Bullish"
				intersect_candle = (candles[-1:0:-1])[a + 15]
				sell_signal += 4
				break
			i = 1
		else:
			intersect_candle = (candles[-1:0:-1])[a + 15]
			if i == -1:
				direction = "Crossed Bearish"
				buy_signal += 4
				break
			elif i == 1:
				direction = "Crossed Bullish"
				sell_signal += 4
				break

	#checks volume of intersection candle to see if "power move" is present
	if len(intersect_candle) == 0:
		print("No double EMA intersection found recently")
		return None
	candle_vol = float(intersect_candle['mid']['o']) - float(intersect_candle['mid']['c'])
	if (candle_vol/float(intersect_candle['mid']['o'])) * 100 > 1:
		if direction == "Crossed Bullish":
			buy_signal += 4
		elif direction == "Crossed Bearish":
			sell_signal += 4
	return {
		'trend': general_trend,
		'buy_signal': buy_signal,
		'sell_signal': sell_signal
	}
	

async def RSI_strategy(market, length):
	buy_signal = 0
	sell_signal = 0
	params = {
		"count": 500,
		"granularity": length
	}
	candles = oanda.request(instruments.InstrumentsCandles(instrument=market, params=params))['candles']
	rsi_sma, rsi_ewma = await RSI(candles, 14)
	cout = 0
	rsi_ewma_arr = rsi_ewma[0].tolist()
	recent_rsi = rsi_ewma_arr[-1:-100:-1]
	# plt.plot(recent_rsi[-1:0:-1])
	# plt.show()
	for i in range(len(recent_rsi)):
		if recent_rsi[i] >= 80:
			if cout == 0:
				sell_signal += 5
			else:
				if recent_rsi[0] < recent_rsi[i]:
					sell_signal += (1/cout) * 2.5 + 2.5
			break
		elif recent_rsi[i] >= 70:
			if cout == 0:
				sell_signal += 4
			else:
				if recent_rsi[0] < recent_rsi[i]:
					sell_signal += (1/cout) * 2 + 2
			break
		elif recent_rsi[i] <= 20:
			if cout == 0:
				buy_signal += 5
			else:
				if recent_rsi[0] > recent_rsi[i]:
					buy_signal += (1/cout) * 2.5 + 2.5
			break
		elif recent_rsi[i] <= 30:
			if cout == 0:
				buy_signal += 4
			else:
				if recent_rsi[0] > recent_rsi[i]:
					buy_signal += (1/cout) * 2 + 2
			break
		cout += 1
	return {
		'buy_signal': buy_signal,
		'sell_signal': sell_signal
	}


#MACD Strategy
async def MACD_strategy(market, length):
	buy_signal = 0.0
	sell_signal = 0.0
	params = {
		"count": 500,
		"granularity": length
	}
	candles = oanda.request(instruments.InstrumentsCandles(instrument=market, params=params))['candles']
	MACD1, signal = await MACD(candles, 80, 40, 9)
	MACD_recent = MACD1[0].tolist()[-1:-100:-1]
	signal_recent = signal[0].tolist()[-1:-100:-1]
	count = 0
	i = 0
	direction = ''
	intersect_candle = []
	for a in range(len(MACD_recent)):
		if MACD_recent[a] < signal_recent[a]:
			if i == 1:
				direction = "Crossed Bearish"
				intersect_candle = (candles[-1:0:-1])[a]
				buy_signal += 4 * 3/count
				break
			i = -1
		elif MACD_recent[a] > signal_recent[a]:
			if i == -1:
				direction = "Crossed Bullish"
				intersect_candle = (candles[-1:0:-1])[a]
				sell_signal += 4 * 3/count
				break
			i = 1
		else:
			intersect_candle = (candles[-1:0:-1])[a]
			if i == -1:
				direction = "Crossed Bearish"
				buy_signal += 4 * 3/count
				break
			elif i == 1:
				direction = "Crossed Bullish"
				sell_signal += 4 * 3/count
				break
		count += 1
	if len(intersect_candle) == 0:
		print("No MACD crossover found recently")
		return None
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
			sum_first += float(candle['mid']['c'])
			num_first += 1
			i += 1
			continue
		if first_after_period:
			sma = sum_first/num_first
			ema = await calc_ema(length, float(candle['mid']['c']), sma)
			prev_ema = ema
			emas.append(ema)
			first_after_period = False
		else:
			ema = await calc_ema(length, float(candle['mid']['c']), prev_ema)
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
	for candle in candles['candles']:
		if i < length:
			length_candles.append(candle)
			i += 1
			continue
		length_candles.append(candle)
		close_prices = []
		for cand in length_candles:
			close_prices.append(cand['mid']['c'])
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


async def RSI(candles, length):
	# print(candles[0])
	close_prices = [float(i['mid']['c']) for i in candles]
	close_df = pd.DataFrame(close_prices)
	delta = close_df.diff()
	# Get rid of the first row, which is NaN since it did not have a previous 
	# row to calculate the differences
	delta = delta[1:] 

	# Make the positive gains (up) and negative gains (down) Series
	up, down = delta.copy(), delta.copy()
	up[up < 0] = 0
	down[down > 0] = 0

	# Calculate the EWMA
	roll_up1 = up.ewm(span=length).mean()
	roll_down1 = down.abs().ewm(span=length).mean()

	# Calculate the RSI based on EWMA
	RS1 = roll_up1 / roll_down1
	RSI1 = 100.0 - (100.0 / (1.0 + RS1))

	# Calculate the SMA
	roll_up2 = up.rolling(length).mean()
	roll_down2 = down.abs().rolling(length).mean()

	# Calculate the RSI based on SMA
	RS2 = roll_up2 / roll_down2
	RSI2 = 100.0 - (100.0 / (1.0 + RS2))

	return RSI1, RSI2


#Calculate the MACD and Signal Line indicators
async def MACD(candles, long_length, short_length, signal_length):
	close_prices = [float(i['mid']['c']) for i in candles]
	close_df = pd.DataFrame(close_prices)
	#Calculate the Short Term Exponential Moving Average
	ShortEMA = close_df.ewm(span=short_length, adjust=False).mean() #AKA Fast moving average
	#Calculate the Long Term Exponential Moving Average
	LongEMA = close_df.ewm(span=long_length, adjust=False).mean() #AKA Slow moving average
	#Calculate the Moving Average Convergence/Divergence (MACD)
	MACD = ShortEMA - LongEMA
	#Calcualte the signal line
	signal = MACD.ewm(span=signal_length, adjust=False).mean()
	return MACD, signal


async def support_resistance(market, candles):
	close_prices = [float(i['mid']['c']) for i in candles]
	data = np.array(close_prices)
	close_series = pd.Series(data)
	(minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs, pmax, maxtrend, maxwindows) = trendln.calc_support_resistance(close_series)
	fig = trendln.plot_support_resistance(close_series)
	plt.savefig('suppres_{}_{}.svg'.format(market, str(datetime.now())), format='svg')
	plt.show()
	plt.clf()
	return minimaIdxs, pmin, mintrend, minwindows, maximaIdxs, pmax, maxtrend, maxwindows





asyncio.get_event_loop().run_until_complete(run())
if __name__ == "__main__":
		run()



