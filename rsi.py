import pandas as pd
import numpy as np
from pandas_datareader import data as web
import matplotlib.pyplot as plt


def get_stock(stock,start,end):
 print(web.DataReader(stock,'google',start,end)['Close'])
 return web.DataReader(stock,'google',start,end)['Close']
 
def RSI(series, period):
 delta = series.diff().dropna()
 u = delta * 0
 d = u.copy()
 u[delta > 0] = delta[delta > 0]
 d[delta < 0] = -delta[delta < 0]
 u[u.index[period-1]] = np.mean( u[:period] ) #first value is sum of avg gains
 u = u.drop(u.index[:(period-1)])
 d[d.index[period-1]] = np.mean( d[:period] ) #first value is sum of avg losses
 d = d.drop(d.index[:(period-1)])
 rs = pd.stats.moments.ewma(u, com=period-1, adjust=False) / \
 pd.stats.moments.ewma(d, com=period-1, adjust=False)
 return 100 - 100 / (1 + rs)
 
df = pd.DataFrame(get_stock('FB', '1/1/2016', '12/31/2016'))
df['RSI'] = RSI(df['Close'], 14)
df.tail()