import ccxtpro
import ccxt
import datetime
import time
import random
from pprint import pprint
import asyncio

#initialize symbol dictionary: keys are symbols, values are list of exchanges that offer that symbol
set_of_symbols = {}

#initial arbmatrices for each symbol: keys are symbols, values are 2-d arrays where rows and columns are symbols and the value in each cell is the spread for buying on row exch and selling on col exch
arbmatrices = {}

async def run():

	await configure_symbols()
	print(set_of_symbols)
	while 1:
		await compute_arbmatrices()
		#For now lets only display one significant arb matrix, will need gui or better way of displaying in future
		market = input("\nWhich symbol would you like to display?")
		while market not in set_of_symbols:
			market = input("Invalid Input: Market not in set of symbols. Which symbol would you like to display?")
		print("\nEXAMPLE SYMBOL: {}".format(market))
		pprint("ARB MATRIX:\n{}".format(arbmatrices[market]))

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


#Configures the set of all possible symbols for inter-exchange arbitrage
async def configure_symbols():
	print("\n\n ----------------------------------- \n\n")
	print("\n\nEsra Inter-Exchange Crypto Arbitrage Finder Running....\n\n")
	print("Copyright 2020 Esra Systems All Rights Reserved visit www.esrainvestments.com for more info\n\n")
	print("\n\n ----------------------------------- \n\n")
	time.sleep(2)

	for exch in ccxtpro.exchanges:
		# filtered_exchanges = [ 'binance', 'coinbase' 'bequant', 'binanceje', 'binanceus', 'bitfinex', 'bitmex', 'bitstamp', 'bittrex', 'bitvavo', 'coinbaseprime', 'coinbasepro', 'ftx', 'gateio', 'hitbtc', 'huobijp',
  #                               'huobipro', 'huobiru', 'kraken', 'kucoin', 'okcoin', 'okex', 'phemex', 'poloniex', 'upbit']
		filtered_exchanges = ['binanceus', 'coinbase', 'poloniex']
		if exch not in filtered_exchanges:
			continue
		if exch == 'binanceus':
			exchange1 = getattr(ccxtpro, 'binanceus')({
				'apiKey': 'nF5CYuh83iNzBfZyqOcyMrSg5l0wFzg5FcAqYhuEhzAbikNpCLSjHwSGXjtYgYWo',
				'secret': 'GaQUTvEurFvYAdFrkFNoHB9jiVyHX9gpaYOnIXPK0C3dugUKr6NHfgpzQ0ZyMfHx',
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
		else:
			exchange1 = getattr(ccxtpro, exch)()
		try:
			await exchange1.load_markets()
		except:
			print("Exchange not loading markets")
			continue
		for sym in exchange1.symbols:
			try:
				if sym in set_of_symbols.keys():
					set_of_symbols[sym].append(exchange1.id)
				else:
					set_of_symbols[sym] = [exchange1.id]
			except e:
				print(e)
		exchange1.close()
	return

#Computes arb matrix for each symbol in set_of_symbols
async def compute_arbmatrices():
	for sym in set_of_symbols:
		arbmatrices[sym] = [[0]*len(set_of_symbols[sym]) for i in range(len(set_of_symbols[sym]))]
		i = 0
		for exch in set_of_symbols[sym]:
			exchange1 = getattr(ccxtpro, exch)()
			try:
				await exchange1.load_markets()
			except:
				print("Exchange not loading markets")
				i += 1
				continue
			try:
				orderbook = await exchange1.fetch_order_book(symbol=sym)
				asks = orderbook['asks']
				min_ask = asks[0]
			except:
				print("Exchange not fetching orderbook or orderbook empty")
				i += 1
				continue
			exchange1.close()
			j = 0
			for exch1 in set_of_symbols[sym]:
				exchange2 = getattr(ccxtpro, exch1)()
				try:
					await exchange2.load_markets()
				except:
					print("Exchange not loading markets")
					j += 1
					continue
				try:
					orderbook1 = await exchange2.fetch_order_book(symbol=sym)
					bids = orderbook1['bids']
					max_bid = bids[0]
					arbmatrices[sym][i][j] = (max_bid[0]-min_ask[0])/max_bid[0]
				except:
					print("Exchange not fetching orderbook or orderbook empty")
					j += 1
					continue
				exchange2.close()
				j += 1
			i += 1
	print("\nFINISHED COMPUTING ARB MATRICES")
	return



asyncio.get_event_loop().run_until_complete(run())


if __name__ == "__main__":
	run()

