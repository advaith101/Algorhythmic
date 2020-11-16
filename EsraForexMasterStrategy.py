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
from oandapyV20.contrib.requests import TrailingStopLossOrderRequest
import trendln
import lstmpredictor

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

#first order since bot start info
first_order = True
first_order_id = "63"

#pandas dataframe where we will be logging realized P/L for all closed orders in real time
trade_log = pd.DataFrame(
        columns = ['_id', 'market', 'position_open_time', 'position_close_time', 'realized_pl_usd', 'realized_pl_pct', 'success']
    )
#Open Positions
open_positions = positions.OpenPositions(accountID = accountID) #OLDEST TO NEWEST TRANSACTION
oanda.request(open_positions)

#buy/sell indicator values for opening a long or short position
long_buy = 3.5
long_sell = 2.5
short_buy = 2.5
short_sell = 3.5

async def run(loop):
    print("\n---------------------Starting master strategy...------------------- \n")
    await asyncio.sleep(3)
    await asyncio.gather(
            scalp(),
            watchman()
        )



### Master Strategy Stuff ###

#NEEDS TO BE DONE (place "DONE" next to it if complete):
#    1. add volatility indicator and refine double ema and rsi strategy
#    (ADDED VOLATILITY INDICATOR: ATR)
#    (DONE - NEEDS REFINING) 2. add support/resistance
#    (DONE - NEEDS REFINING) 3. add MACD
#    4. add points of value strategy
#    5. get feedback - log P/L's and strategy scores for each position once it is closed. This will be used as a learner.
#    6. add Randomized Weighted Majority Algorithm to optimize weights for strategies over time
#    7. Exponential Trailing stop loss

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
        ATR_score = await ATR_strategy(market, "H1")
        points_of_val_score = await points_of_value(market, "H1")

        ### This section is for LSTM Neural Network that will predict the next price
        params = {
            "count": 500,
            "granularity": "H1"
            }
        candles = oanda.request(instruments.InstrumentsCandles(instrument=market, params=params))['candles']
        df = pd.DataFrame(
                columns=["Date", "Open", "High", "Low", "Close", "Volume"]
            )
        df['Date'] = [i['time'] for i in candles]
        df['Open'] = [float(i['mid']['o']) for i in candles]
        df['High'] = [float(i['mid']['h']) for i in candles]
        df['Low'] = [float(i['mid']['l']) for i in candles]
        df['Close'] = [float(i['mid']['c']) for i in candles]
        df['Volume'] = [float(i['volume']) for i in candles]
        last_val, next_val = lstmpredictor.lstm_neural_network(df)
        print(last_val, next_val)
        ###

        print("\nMARKET: {}".format(market))
        print("RSI score: {}".format(rsi_h1_score))
        print("double EMA score: {}".format(double_ema_score))
        print("MACD score: {}".format(MACD_score))
        print("ATR score: {}".format(ATR_score))
        print("Points of Value score: {}".format(points_of_val_score))
        scores_by_market[i]['strategy_scores'].extend([rsi_h1_score, double_ema_score, MACD_score, ATR_score])
        overallscore = {}
        buy = 0
        sell = 0
        count = 0
        ## Apply Randomized Weighted Majority Algo here to optimize the weights of each strategy over time
        for strategyscore in scores_by_market[i]['strategy_scores']:
            try:
                buy += strategyscore['buy_signal']
                sell += strategyscore['sell_signal']
            except:
                if buy > sell:
                    buy += strategyscore['enter_signal']
                    buy -= strategyscore['exit_signal']
                elif sell > buy:
                    sell += strategyscore['enter_signal']
                    sell -= strategyscore['exit_signal']
            count += 1
        overallscore['buy_signal'] = buy/count
        overallscore['sell_signal'] = sell/count
        scores_by_market[i]['overall_score'] = overallscore
        if (overallscore['buy_signal'] > long_buy and overallscore['sell_signal'] < long_sell):
            print("\nFOUND LONG PROFITABLE TRADE OPPORTUNITY---------------")
            buy(market, 'long', 10) #10 refers to amount of money wanted to invest
            print("OVERALL SCORE: {}".format(overallscore))
            if order_mode:
                market_order, trailing_stop = await asyncio.ensure_future(create_order(scores_by_market[i]['market'], overallscore['buy_signal'], overallscore['sell_signal']))
                order_id = market_order['orderFillTransaction']['orderID']
                if first_order:
                    first_order_id = order_id
                    first_order = False
                await asyncio.ensure_future(watch_order(order_id))
        elif (overallscore['buy_signal'] < short_buy and overallscore['sell_signal'] > short_sell):
            print("\nFOUND SHORT PROFITABLE TRADE OPPORTUNITY---------------")
            buy(market, indicators_dict, 'short')
            print("OVERALL SCORE: {}".format(overallscore))
        i += 1
    return scores_by_market


#Watchman function watches transaction history continuosly, in parallel, to ensure nothing crazy happens. Also logs all the orders and realized/unrealized P/L.
#UPDATE - Logging P/L complete. Need to finish alert system although with the trailing stop I dont think there will be a need.
async def watchman():
    while 1:
        params = {
            "sinceTransactionID": int(first_order_id)
        }
        account_info = oanda.request(accounts.AccountChanges(accountID, params=params))
        account_state = account_info['state']
        account_changes = account_info['changes']
        open_positions = account_state['positions']
        recently_opened_positions = account_changes['tradesOpened']
        recently_closed_positions = account_changes['tradesClosed']
        #add recent additions to trade log
        recent_additions = []
        for closed_pos in recently_closed_positions:
            if closed_pos['realizedPL'][0] == '-':
                success = False
            else:
                success = True
            pct = float(closed_pos['realizedPL'])/float(closed_pos['initialUnits'])
            recent_additions.append([closed_pos['id'], closed_pos['instrument'], closed_pos['openTime'], str(datetime.datetime.now()), closed_pos['realizedPL'], str(pct), success])
        for update in recent_additions:
            update_df = pd.DataFrame(
                    data=update,
                    columns=['_id', 'market', 'position_open_time', 'position_close_time', 'realized_pl_usd', 'realized_pl_pct', 'success']
                )
            trade_log.append(update_df, ignore_index=True)
        # print(trade_log)
        #NEEDS TO BE DONE - Watch for huge losses, incoming margin closeout, or any other discrepencies     
        await asyncio.sleep(3)
    pass


#function that monitors price for a market that we've opened a new position for and sells when it detects reversal
async def watch_order(order_id):
    #needs to be completed
    pass

def buy(market, positionType, positionSize): #positionSize in Dollars (Amount of Money Plan on Investing)
    if (positionType == 'long'):
        response = oanda.get_prices(instruments=market)
        prices = response.get("prices")
        bidding_price = prices[0].get("bid")
        buy_units = (int) (positionSize / bidding_price);

        trade_expire = datetime.utcnow() + timedelta(days=1)
        trade_expire = trade_expire.isoformat("T") + "Z"
        response = oanda.create_order(account_id,
            instrument=market,
            units=buy_units,
            side='buy',
            type='limit',
            price=bidding_price,
            expiry=trade_expire
        )
    else:
        response = oanda.get_prices(instruments=market)
        prices = response.get("prices")
        asking_price = prices[0].get("ask")
        sell_units = (int) (positionSize / asking_price);

        trade_expire = datetime.utcnow() + timedelta(days=1)
        trade_expire = trade_expire.isoformat("T") + "Z"
        response = oanda.create_order(account_id,
            instrument=market,
            units=sell_units,
            side='sell',
            type='limit',
            price=asking_price,
            expiry=trade_expire
        )

         
def findOpenPositionMarkets():
    markets = []
    for i in range(0, len(open_positions.response.get('positions'))):
        markets.append(open_positions.response.get('positions')[i].get('instrument', 0))
    return markets

#Function to order based on overall score for 1 market - NEED to finish expononential trailing stop and reducing order size as order goes in our direction (hedging)
async def create_order(market, buy_signal, sell_signal):
    # if buy_signal > sell_signal:
    #     mo = MarketOrderRequest(instrument=market, units=(buy_signal * 10000 - sell_signal * 10000))
    #     market_order = oanda.request(orders.OrderCreate(accountID, data=mo.data))
    # elif sell_signal > buy_signal:
    #     mo = MarketOrderRequest(instrument=market, units=(buy_signal * 10000 - sell_signal * 10000))
    mo = MarketOrderRequest(instrument=market, units=(buy_signal * 10000 - sell_signal * 10000))
    market_order = oanda.request(orders.OrderCreate(accountID, data=mo.data))
    #order confirmation
    print(json.dumps(market_order, indent=4))
    #set trailing stop
    order_id = market_order['orderFillTransaction']['orderID']
    ordr = TrailingStopLossOrderRequest(tradeID=order_id, distance=20)
    trailing_stop = oanda.request(orders.OrderCreate(accountID, data=ordr.data))
    #trailing stop confimrmation
    print(json.dumps(trailing_stop, indent=4))

    return market_order, trailing_stop






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
    emas_short = (await calc_emas(candles, 5)).tolist()[-1:0:-1]
    emas_medium = (await calc_emas(candles, 15)).tolist()[-1:0:-1]
    emas_long = (await calc_emas(candles, 75)).tolist()[-1:0:-1]
    i = 0
    direction = ""
    for a in range(len(emas_medium)):
        if emas_short[a] < emas_medium[a]:
            if i == 1:
                direction = "Crossed Bearish"
                intersect_candle = (candles[-1:0:-1])[a]
                buy_signal += 3
                break
            i = -1
        elif emas_short[a] > emas_medium[a]:
            if i == -1:
                direction = "Crossed Bullish"
                intersect_candle = (candles[-1:0:-1])[a]
                sell_signal += 3
                break
            i = 1
        else:
            intersect_candle = (candles[-1:0:-1])[a]
            if i == -1:
                direction = "Crossed Bearish"
                buy_signal += 3
                break
            elif i == 1:
                direction = "Crossed Bullish"
                sell_signal += 3
                break
    direction1 = ""
    intersect_candle1 = []
    for a in range(len(emas_medium)):
        if emas_medium[a] < emas_long[a]:
            if i == 1:
                direction1 = "Crossed Bearish"
                intersect_candle1 = (candles[-1:0:-1])[a]
                buy_signal += 3
                break
            i = -1
        elif emas_medium[a] > emas_long[a]:
            if i == -1:
                direction1 = "Crossed Bullish"
                intersect_candle1 = (candles[-1:0:-1])[a]
                sell_signal += 3
                break
            i = 1
        else:
            intersect_candle1 = (candles[-1:0:-1])[a]
            if i == -1:
                direction1 = "Crossed Bearish"
                buy_signal += 3
                break
            elif i == 1:
                direction1 = "Crossed Bullish"
                sell_signal += 3
                break

    #checks volume of intersection candle to see if "power move" is present
    if len(intersect_candle1) == 0:
        print("No EMA 15 - EMA 75 intersection found recently")
        if len(intersect_candle) == 0:
            print('No EMA 5 - EMA 15 intersection found recently')
            return None
    if direction1 == direction:
        if direction == "Crossed Bullish":
            sell_signal += 2
        elif direction == "Crossed Bearish":
            buy_signal += 2
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


#MACD Strategy for crossover only
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


#Average True Range (good for checking if good time to enter market) - Enter the market when ATR recently was at local minima, exit if ATR is too high
async def ATR_strategy(market, length):
    enter_signal = 0.0
    exit_signal = 0.0
    params = {
        "count": 500,
        "granularity": length
    }
    candles = oanda.request(instruments.InstrumentsCandles(instrument=market, params=params))['candles']
    atr = await ATR(market, candles, 50)
    # print(type(atr), atr)
    atr_recent = atr.tolist()[-1:-100:-1]
    max_atr = max(atr_recent)
    min_atr = min(atr_recent)
    if (atr_recent[0] - min_atr)/min_atr < 0.015:
        enter_signal += 3
        if (atr_recent[0] - min_atr)/min_atr < 0.09:
            enter_signal += 2
    elif abs((atr_recent[0] - max_atr)/max_atr) < 0.015:
        exit_signal += 3
        if abs((atr_recent[0] - max_atr)/max_atr) < 0.09:
            exit_signal += 2
    return {
        'enter_signal': enter_signal,
        'exit_signal': exit_signal
    }


#points of value - needs to be finished
async def points_of_value(market, length):
    enter_signal = 0.0
    exit_signal = 0.0
    params = {
        "count": 500,
        "granularity": length
    }
    candles = oanda.request(instruments.InstrumentsCandles(instrument=market, params=params))['candles']
    #await support_resistance(market, candles)
    return {
        'enter_signal': enter_signal,
        'exit_signal': exit_signal
    }




#Below are indicators that we will be using in our strategies


#Calculates EMA's for each set of candles (ie if you plot it it would be the EMA)
async def calc_emas(candles, length):
    close_prices = [float(i['mid']['c']) for i in candles]
    df = pd.Series(close_prices)
    emas = df.ewm(span=length).mean()
    #print(emas)
    return emas



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


#finds all support/resistance levels and support/resistance trendlines
async def support_resistance(market, candles):
    close_prices = [float(i['mid']['c']) for i in candles]
    data = np.array(close_prices)
    close_series = pd.Series(data)
    (minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs, pmax, maxtrend, maxwindows) = trendln.calc_support_resistance(close_series)
    fig = trendln.plot_support_resistance(close_series, numbest=2)
    # plt.savefig('suppres_{}_{}.svg'.format(market, str(datetime.datetime.now())), format='svg')
    # plt.show()
    plt.clf()
    return minimaIdxs, pmin, mintrend, minwindows, maximaIdxs, pmax, maxtrend, maxwindows


#finds average true range for set of candles
async def ATR(market, candles, length):
    open_prices = np.array([float(i['mid']['o']) for i in candles])
    close_prices = np.array([float(i['mid']['c']) for i in candles])
    highs = np.array([float(i['mid']['h']) for i in candles])
    lows = np.array([float(i['mid']['l']) for i in candles])
    df = pd.DataFrame({
            'open_prices': open_prices,
            'close_prices': close_prices,
            'highs': highs,
            'lows': lows
        })
    high = df['highs']
    low = df['lows']
    close = df['close_prices']
    df['tr0'] = abs(high - low)
    df['tr1'] = abs(high - close.shift())
    df['tr2'] = abs(low - close.shift())
    tr = df[['tr0', 'tr1', 'tr2']].max(axis=1)
    atr = tr.ewm(alpha=1/length, adjust=False).mean()
    return atr



open_positions_watchlist = findOpenPositionMarkets()
loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))
if __name__ == "__main__":
        run()
