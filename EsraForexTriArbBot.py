import ccxtpro
import ccxt
#from datetime import datetime, timedelta
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
import csv
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

#setting up start times
current = datetime.datetime.now()
current_time = current.time()

#csv storage instantiation
csvName = str(current_time) + '.csv'
with open(csvName, 'w') as f:
    fieldnames = ['Bot_Start_Date', 'Bot_Start_Time', 'Arb_Time', 'Exchange', 'Initial_USD', 'First_Market', 'Second_Market', 'Third_Market', 'Spread', 'Estimated_Profit']
    thewriter = csv.DictWriter(f, fieldnames = fieldnames)
    thewriter.writeheader()


    async def run():
        #triarb strategy
        tri_arbs = await config_arbitrages()
        print("\n\n---------------TRIANGULAR ARBITRAGRE CONFIGURATION FINISHED---------------\n\n")
        x = input("Now finding which arbs are profitable. Do you want to place actual orders? (y/n)")
        order_mode = False
        if x == 'y':
            order_mode = True
        count = 0
        for arb in tri_arbs:
            b = await execute_tri_arb(arb, order_mode, count)
            if not b:
                count += 1
        print("\n-------------------------TRIANGULAR ARBITRATION FINISHED------------------------------\n")


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
            print("DEPTH: {}".format(depth))
            # if order_mode:
            #     #Create order here - needs to be finished
            #     funds = await get_available_funds()
            #     if count == 0:
            #         order1, order2, order3 = await asyncio.ensure_future(create_triarb_order(arb_list, prices, funds))
            arbitrageopp = {
                'spread': profit,
                'initialUSD': depth,
                'sym_list': arb_list,
                'estimated_profit': profit * depth
            }
            writeToCSV(arbitrageopp)
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

    def writeToCSV(arbitrageopp):
      i = 0
      if (i == 0):
          thewriter.writerow({'Bot_Start_Date': current.date(), 'Bot_Start_Time': current.time(), 'Arb_Time': current.now(), 'Exchange': 'Oanda', 'Initial_USD': arbitrageopp['initialUSD'], 'First_Market': arbitrageopp['sym_list'] [0], 'Second_Market': arbitrageopp['sym_list'] [1], 'Third_Market': arbitrageopp['sym_list'] [2], 'Spread': arbitrageopp['spread'], 'Estimated_Profit': arbitrageopp['estimated_profit']})
      else:
          thewriter.writerow({'Arb_Time': current.now(), 'Exchange': 'Oanda', 'Initial_USD': arbitrageopp['initialUSD'], 'First_Market': arbitrageopp['sym_list'] [0], 'Second_Market': arbitrageopp['sym_list'] [1], 'Third_Market': arbitrageopp['sym_list'] [2], 'Spread': arbitrageopp['spread'], 'Estimated_Profit': arbitrageopp['estimated_profit']})
      i+=1

    asyncio.get_event_loop().run_until_complete(run())
    if __name__ == "__main__":
            run()
