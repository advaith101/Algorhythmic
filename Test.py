import csv
import asyncio
import datetime
import random
# import oandapyV20.endpoints.accounts as accounts
# import oandapyV20.endpoints.positions as positions
import pprint
import json
import requests



marketsSummary = requests.get("https://trade.mandala.exchange/open/v1/common/symbols")
marketsJson = marketsSummary.json()
symbols = []
for singleMarket in marketsJson['data']['list']:
    symbols.append(singleMarket['symbol'])

print (symbols)


# orderBook = requests.get("https://trade.mandala.exchange/open/v1/market/depth?symbol=" + "MDX_USDT")
# orderBookJson = orderBook.json()
# depth = orderBookJson['data']
# for bid in depth['bids']:
#     print(bid[0])

# USDTorderBook = requests.get("https://trade.mandala.exchange/open/v1/market/depth?symbol=" + 'BTC_USDT')
# USDTorderBookJson = USDTorderBook.json()
# USDTdepth = USDTorderBookJson['data']
# dollar_exchrate = USDTdepth['bids'][0][0]
# print(dollar_exchrate)




# # print(datetime.datetime.now())
# # current_time = datetime.datetime.now().time()
# # csvName = str(current_time) + ".csv"
# # print(csvName)
# # with open('triarbdata.csv', 'w') as f:
# #
# #     fieldnames = ['Bot Start Date', 'Bot Start Time', 'Arb Time','Exchange', 'Initial USD', 'First Market', 'Second Market', 'Third Market', 'Spread', 'Estimated Profit']
# #     thewriter = csv.DictWriter(f, fieldnames = fieldnames)
# #     thewriter.writeheader()
# #     current_time = datetime.datetime.now()
# #
# #     def writeToCSV(arbitrageopp):
# #         i = 0
# #         if (i == 0):
# #             thewriter.writerow({'Bot Start Date': current_time.date(), 'Bot Start Time': current_time.time(), 'Arb Time': current_time.now(), 'Exchange': arbitrageopp['exchange'], 'Initial USD': arbitrageopp['initialUSD'], 'First Market': arbitrageopp['sym_list'] [0], 'Second Market': arbitrageopp['sym_list'] [1], 'Third Market': arbitrageopp['sym_list'] [2], 'Spread': arbitrageopp['spread'], 'Estimated Profit': arbitrageopp['estimated_profit']})
# #         else:
# #             thewriter.writerow({'Arb Time': current_time.now(), 'Exchange': arbitrageopp['exchange'], 'Initial USD': arbitrageopp['initialUSD'], 'First Market': arbitrageopp['sym_list'] [0], 'Second Market': arbitrageopp['sym_list'] [1], 'Third Market': arbitrageopp['sym_list'] [2], 'Spread': arbitrageopp['spread'], 'Estimated Profit': arbitrageopp['estimated_profit']})
# #         i+=1
# #     arbitrage = {
# #         'exchange': 'Binance',
# #         'sym_list': ['BTC/USD', 'BTC/ETH', 'ETH/USD'],
# #         'initialUSD': 200,
# #         'spread': .2,
# #         'estimated_profit': 300,
# #     }
# #
# #     writeToCSV(arbitrage)
# #account info for practice acct.
# accountID = "101-001-16023947-001"
# access_token = "9a5cae7cbfacf5f6aa634097bc1bc337-b394ef6856186107ebfdc589260269bf"

# # oanda = API(environment="live", access_token=access_token)
# oanda = API(access_token=access_token)
# fee_pct = 0.0 # YESSIRRR OANDA IS FREE COMMISSION

# client = API(access_token=access_token)
# # r = accounts.AccountSummary(accountID)
# # client.request(r)
# # print(r.response)

# a = positions.OpenPositions(accountID = accountID)
# client.request(a)
# pp = pprint.PrettyPrinter(indent=4)
# #pp.pprint(a.response.get('positions', 0))
# print(a.response.get('positions')[0])



# def findOpenPositionMarkets():
#     markets = []
#     for i in range(0, len(a.response.get('positions'))):
#         markets.append(a.response.get('positions')[i].get('instrument', 0))
#     return markets

# markets2 = findOpenPositionMarkets()
# #pp.pprint(markets2)
# print(type(markets2))



# def print_positions(positions, open_only=True):
#     """
#     Print a list of Positions in table format.
#     Args:
#         positions: The list of Positions to print
#         open_only: Flag that controls if only open Positions are displayed
#     """

#     filtered_positions = [
#         p for p in positions 
#         if not open_only or p.long.units != "0" or p.short.units != "0"
#     ]

#     if len(filtered_positions) == 0:
#         return

#     #
#     # Print the Trades in a table with their Instrument, realized PL,
#     # unrealized PL long postion summary and shor position summary
#     #
#     common.view.print_collection(
#         "{} {}Positions".format(
#             len(filtered_positions),
#             "Open " if open_only else ""
#         ),
#         filtered_positions,
#         [
#             ("Instrument", lambda p: p.instrument),
#             ("P/L", lambda p: p.pl),
#             ("Unrealized P/L", lambda p: p.unrealizedPL),
#             ("Long", position_side_formatter("long")),
#             ("Short", position_side_formatter("short")),
#         ]
#     )

#     print("")
