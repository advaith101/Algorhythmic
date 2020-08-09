import csv
import datetime
import random
from fractions import Fraction
from math import gcd
from functools import reduce
from pprint import pprint


def findDepthForWholeUnitsTrading(exch_rate_1, exch_rate_2, exch_rate_3):
    multiplied_x_y = exch_rate_1 * exch_rate_2
    multiplied_x_y_z = exch_rate_1 * exch_rate_2 * exch_rate_3
    denominator_1 = str(Fraction(exch_rate_1).limit_denominator()).split('/') [1]
    print(denominator_1)
    denominator_2 = str(Fraction(multiplied_x_y).limit_denominator()).split('/') [1]
    print(denominator_2)
    denominator_3 = str(Fraction(multiplied_x_y_z).limit_denominator()).split('/') [1]
    print(denominator_3)
    denominators = [int(denominator_1), int(denominator_2), int(denominator_3)]
    return LCM(denominators)

def LCM(denominators):   #will work for an int array of any length
    return reduce(lambda a,b: a*b // gcd(a,b), denominators)

print(findDepthForWholeUnitsTrading(1.62, .132, .733))
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
