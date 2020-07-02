import ccxtpro
import time
import matplotlib.pyplot as plt
import random
from pprint import pprint
import asyncio


async def run():
	# exchange = ccxtpro.binance()
	# await exchange.load_markets()
	# test = exchange.symbols
	# print(test)

	await arbitrage()


async def arbitrage(cycle_num=5, cycle_time=1):
	print("\n\n ----------------------------------- \n\n")
	print("\n\n Esra Unified Crypto Arbitrage Finder Running....\n\n")
	print("Copyright 2020 Esra Systems All Rights Reserved")
	time.sleep(2)
	fee_percentage = 0.001          #divided by 100

	for exch in ccxtpro.exchanges:    #initialize Exchange
		exchange1 = getattr (ccxtpro, exch) () 
		try:
			await exchange1.load_markets()
		except:
			print('oh well')
		print(exchange1)
		symbols = exchange1.symbols
		print(symbols)
		if symbols is None:
			print("Skipping Exchange ", exch)
			print("\n-----------------\nNext Exchange\n-----------------")
		elif len(symbols)<30:
			print("\n-----------------\nNeed more Pairs (Next Exchange)\n-----------------")
		else:
			print(exchange1)

			exchange1_info = dir(exchange1)
			print("------------Exchange: ", exchange1.id)
			# pprint(exchange1_info)
			print(exchange1.symbols)    #List all currencies
			time.sleep(5)
			
			list_of_arb_lists = []	#List of all arb triangles
			for symb in symbols:
				arb_list = [symb]
				print(arb_list)
				# Find 'triangle' of currency rate pairs
				j=0
				proceed = True
				while proceed:
					print('hello')
					if j >= 1:
						if len(arb_list) > 1:
							print
							final = arb_list[0].split('/')[1]  + '/' + str(arb_list[1].split('/')[1])
							print(final)
							# if final in symbols:
							arb_list.append(final)
							print('hey')
							break
						else: 

							break

					for sym in symbols[1:]:
						# print('reached')
						if sym in arb_list:
							print('OKBUDDYYY')
							pass
						else:
							if j % 2 == 0:
								# print("{} , {}".format(arb_list[j][0:3], sym[0:3]))
								if arb_list[j].split('/')[0] == sym.split('/')[0]:
									print('EASYMONNNEEYYY')
									if arb_list[j] == sym:
										print('HOLLAAAA')
										pass
									else:
										arb_list.append(sym)
										print(arb_list)
										j+=1
										print('hi')
										break
								else:
									pass
							if j % 2 == 1:
								if arb_list[j].split(',')[1] == sym.split(',')[1]:
									if arb_list[j] == sym:
										pass
									else:
										arb_list.append(sym)
										print(arb_list)
										j+=1
										print('ho')
										break
								else:
									pass
					j+=1
					# proceed = False
				if len(arb_list) > 2:
					list_of_arb_lists.append(arb_list)
			print("List of Arbitrage Symbols:", list_of_arb_lists)
			
			for arb_list in list_of_arb_lists:
				# Determine Rates for our 3 currency pairs - order book
				list_exch_rate_list = []
				for k in range(0,1):
					i=0
					exch_rate_list = []
					print("Cycle Number: ", k)
					for sym in arb_list:
						print(sym)
						if sym in symbols:
							depth = await exchange1.fetch_order_book(symbol=sym)
							# pprint(depth)
							if i % 2 == 0:
								try:
									exch_rate_list.append(depth['bids'][0][0])
								except:
									exch_rate_list.append(0)
							else:
								try:
									exch_rate_list.append(depth['asks'][0][0])
								except:
									print('YOOOOOOOOLOLIJSAODIFHASOID')
									exch_rate_list.append(0)
							i+=1
						else:
							print("OHHHHHHH")
							exch_rate_list.append(0)
					# exch_rate_list.append(((rateB[-1]-rateA[-1])/rateA[-1])*100)  #Expected Profit
					exch_rate_list.append(time.time())      #change to Human Readable time
					print(exch_rate_list)
					# Compare to determine if Arbitrage opp exists
					try:
						if exch_rate_list[0]<exch_rate_list[1]/exch_rate_list[2]:
							# calculate real rate!!!
							exchangeratespread = (exch_rate_list[1]/exch_rate_list[2]) - exch_rate_list[0]
							#
							print("Arbitrage Possibility")
						else:
							print("No Arbitrage Possibility")
					except:
						print("No Arbitrage Possibility")
					# Format data (list) into List format (list of lists)
					list_exch_rate_list.append(exch_rate_list)
					time.sleep(cycle_time)
				print(list_exch_rate_list)
				# Create list from Lists for matplotlib format


				rateA = 0.0      #Original Exchange Rate
				rateB = 0.0     #Calculated/Arbitrage Exchange Rate
				rateB_fee = 0.0  #Include Transaction Fee
				price1 = 0.0   #List for Price of Token (Trade) 1
				price2 = 0.0   #List for price of Token (Trade) 2
				time_list = 0.0  #time of data collection
				profit = 0.0     #Record % profit
				try:
					for rate in list_exch_rate_list:
						rateA = (rate[0])
						rateB = (rate[1]/rate[2])
						rateB_fee = ((rate[1]/rate[2])*(1-fee_percentage)*(1-fee_percentage))
						price1 = (rate[1])
						price2 =(rate[2])
						profit = (rateB-rateA)/rateA - .003
						time_list = rate[3]
					print("Original Exchange Rate: {} \n Arbitrage Exchange Rate: {} \n Arbitrage Exchange Rate including Fees: {} \n Real Profit: {}".format(rateA, rateB, rateB_fee, profit))
				except:
					print("No Arbitrage Possibility")

		exchange1.close()

asyncio.get_event_loop().run_until_complete(run())


if __name__ == "__main__":
	run()






























