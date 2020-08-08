import csv
import datetime
import random
from pprint import pprint
print(datetime.datetime.now())
current_time = datetime.datetime.now().time()
csvName = str(current_time) + ".csv"
print(csvName)
# with open('triarbdata.csv', 'w') as f:
#
#     fieldnames = ['Bot Start Date', 'Bot Start Time', 'Arb Time','Exchange', 'Initial USD', 'First Market', 'Second Market', 'Third Market', 'Spread', 'Estimated Profit']
#     thewriter = csv.DictWriter(f, fieldnames = fieldnames)
#     thewriter.writeheader()
#     current_time = datetime.datetime.now()
#
#     def writeToCSV(arbitrageopp):
#         i = 0
#         if (i == 0):
#             thewriter.writerow({'Bot Start Date': current_time.date(), 'Bot Start Time': current_time.time(), 'Arb Time': current_time.now(), 'Exchange': arbitrageopp['exchange'], 'Initial USD': arbitrageopp['initialUSD'], 'First Market': arbitrageopp['sym_list'] [0], 'Second Market': arbitrageopp['sym_list'] [1], 'Third Market': arbitrageopp['sym_list'] [2], 'Spread': arbitrageopp['spread'], 'Estimated Profit': arbitrageopp['estimated_profit']})
#         else:
#             thewriter.writerow({'Arb Time': current_time.now(), 'Exchange': arbitrageopp['exchange'], 'Initial USD': arbitrageopp['initialUSD'], 'First Market': arbitrageopp['sym_list'] [0], 'Second Market': arbitrageopp['sym_list'] [1], 'Third Market': arbitrageopp['sym_list'] [2], 'Spread': arbitrageopp['spread'], 'Estimated Profit': arbitrageopp['estimated_profit']})
#         i+=1
#     arbitrage = {
#         'exchange': 'Binance',
#         'sym_list': ['BTC/USD', 'BTC/ETH', 'ETH/USD'],
#         'initialUSD': 200,
#         'spread': .2,
#         'estimated_profit': 300,
#     }
#
#     writeToCSV(arbitrage)
