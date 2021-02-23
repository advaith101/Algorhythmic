#import ccxt
import requests
import datetime
import time
import random
from pprint import pprint
import asyncio
import requests

amount_digits_rounded = 5
percentUncertaintyOverAverage = .3


async def run():
    # exchange = ccxtpro.binance()
    # await exchange.load_markets()
    # test = exchange.symbols
    # print(test)

    list_of_lists_of_arb_lists = await config_arbitrages()
    while 1:
        profit_spread_list, profit_dollars_list, market_depth_dollars_list = await execute_all_tri_arb_orders(list_of_lists_of_arb_lists)
        await compute_avg_spread(profit_spread_list, profit_dollars_list, market_depth_dollars_list)
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
        # print("CYCLE FINISHED, STARTING NEXT CYCLE...")
        # await asyncio.sleep(3)
    print("\n\nEsra CryptoBot has finished running\n\n")

async def config_arbitrages():
    print("\n\n ----------------------------------- \n\n")
    print("\n\nEsra Unified Crypto Arbitrage Finder Running....\n\n")
    print("Copyright 2020 Esra Systems All Rights Reserved visit www.esrainvestments.com for more info\n\n")
    print("\n\n ----------------------------------- \n\n")
    time.sleep(2)
    markets = {}
    list_of_lists_of_arb_lists = []

    print("Exchange Name: {}".format('Mandala Exchange'))
    #New API Request
    marketsSummary = requests.get("https://trade.mandala.exchange/open/v1/common/symbols")
    marketsJson = marketsSummary.json()
    symbols = []
    for singleMarket in marketsJson['data']['list']:
        symbols.append(singleMarket['symbol'])

    print(symbols)  # List all currencies
    # time.sleep(5)
    exchange = {
        name: 'Mandala Exchange',
        symbols: symbols
    }
    list_of_arb_lists = []  # List of all arb triangles
    list_of_arb_listswmarkets = []
    for symb in symbols:
        arb_list = [symb]
        # print(arb_list)
        # Find 'triangle' of currency rate pairs
        j = 0
        proceed = True
        while proceed:
            # print('hello')
            if j >= 1:
                if len(arb_list) > 1:
                    final = arb_list[0].split('/')[1] + '/' + str(arb_list[1].split('/')[1])
                    # print(final)
                    # if final in symbols:
                    arb_list.append(final)
                    break
                else:

                    break

            for sym in symbols[1:]:
                # print('reached')
                if sym in arb_list:
                    pass
                else:
                    if j % 2 == 0:
                        # print("{} , {}".format(arb_list[j][0:3], sym[0:3]))
                        if arb_list[j].split('/')[0] == sym.split('/')[0]:
                            if arb_list[j] == sym:
                                pass
                            else:
                                arb_list.append(sym)
                                j += 1
                                break
                        else:
                            pass
                    if j % 2 == 1:
                        if arb_list[j].split(',')[1] == sym.split(',')[1]:
                            if arb_list[j] == sym:
                                pass
                            else:
                                arb_list.append(sym)
                                # print(arb_list)
                                j += 1
                                print('ho')
                                break
                        else:
                            pass
            j += 1
            # proceed = False
        if len(arb_list) > 2:
            if arb_list[0] in markets and arb_list[1] in markets and arb_list[2] in markets:
                print(arb_list)
                list_of_arb_lists.append(arb_list)

        print("\nList of Arbitrage Symbols:", list_of_arb_lists)
        list_of_lists_of_arb_lists.append([exchange1, list_of_arb_lists, markets])
        return list_of_lists_of_arb_lists



async def execute_all_tri_arb_orders(list_of_lists_of_arb_lists):
    #Determines profitability and executes profitable orders.
    profit_spread_list = []
    profit_dollars_list = []
    market_depth_dollars_list = []
    for list_of_arb_lists in list_of_lists_of_arb_lists:
        exchange = list_of_arb_lists[0]
        markets = list_of_arb_lists[2]
        for arb_list in list_of_arb_lists[1]:
            # print("{} \n".format(exchange1))
            # print("{} \n".format(markets))
            # print("{} \n".format(arb_list))
            # arbitrageopp = asyncio.gather(await find_tri_arb_opp(exchange1, list(markets), arb_list))
            arbitrageopp = await find_tri_arb_opp(exchange, markets, arb_list)
            try:
                if arbitrageopp['profit'] > 0.0:
                    if arb_list[0][-3:] == 'BUSD':
                        profit_spread_list.append(arbitrageopp['profit'])
                        profit_dollars_list.append(arbitrageopp['profit_in_dollars'])
                        market_depth_dollars_list.appned(arbitrageopp['market_depth_dollars'])
                        quantity_list = arbitrageopp['quantity_list']
                        quantity_3 = tri_arb_orders(arbitrageopp['exchange'], arbitrageopp['exch_rate_list'], arbitrageopp['sym_list'], arbitrageopp['quantity_list'], arbitrageopp['fee_percentage'])
                        await post_tri_arb_USD_transfer(arbitrageopp['exchange'],  arbitrageopp['sym_list'], arbitrageopp['fee_percentage'], quantity_3)
                    else:
                        profit_spread_list.append(arbitrageopp['profit'])
                        profit_dollars_list.append(arbitrageopp['profit_in_dollars'])
                        market_depth_dollars_list.appned(arbitrageopp['market_depth_dollars'])
                        quantity_list = arbitrageopp['quantity_list']
                        await pre_tri_arb_USD_transfer(arbitrageopp['exchange'], arbitrageopp['sym_list'], arbitrageopp['fee_percentage'], quantity_list[0])
                        quantity_3 = tri_arb_orders(arbitrageopp['exchange'], arbitrageopp['exch_rate_list'], arbitrageopp['sym_list'], arbitrageopp['quantity_list'], arbitrageopp['fee_percentage'])
                        await post_tri_arb_USD_transfer(arbitrageopp['exchange'],  arbitrageopp['sym_list'], arbitrageopp['fee_percentage'], quantity_3)
                        print("\nOrdering should be complete by this point\n")
            except:
                print("\n\nNo Arbitrage Possibility\n\n")
    return profit_spread_list, profit_dollars_list, market_depth_dollars_list


async def find_tri_arb_opp(exchange, total_markets, arb_list, fee_percentage = .002):
    # Determine Rates for our 3 currency pairs - order book
    await exchange.load_markets()
    opp_exch_rate_list = []
    opp_quantity_list = []
    opp_max_bid_price_quantity = []
    list_exch_rate_list = []
    exch_rate_list = []
    dollar_exchrate = 0.0
    i = 0
    print("\nChecking for profit: ")
    for sym in arb_list:
        # print(sym)
        if sym in exchange.symbols:
            if i % 2 == 0:
                opp_max_bid_price_quantity = await maxBid(exchange, sym, total_markets, i)
                # assumed trade volume of $100
                if opp_max_bid_price_quantity['isFound']:
                    exch_rate_list.append(opp_max_bid_price_quantity['bid_price'])
                    print("Max Bid Price: {}".format(opp_max_bid_price_quantity['bid_price']))
                    opp_quantity_list.append(opp_max_bid_price_quantity['bid_quantity'])
                    if i == 0:
                        dollar_exchrate = opp_max_bid_price_quantity['dollar_exchrate']
                    # opp_max_bid_price_quantity['bid_quantity']
                else:
                    print("\nCould not find a bid_price or bid_quantity\n")
                    break
                    exch_rate_list.append(0)
            else:
                opp_min_ask_price_quantity = await minAsk(exchange, sym, total_markets)
                # assumed trade volume of $100
                if opp_min_ask_price_quantity['isFound']:
                    exch_rate_list.append(opp_min_ask_price_quantity['ask_price'])
                    print("Min Ask Price: {}".format(opp_min_ask_price_quantity['ask_price']))
                    opp_quantity_list.append(opp_min_ask_price_quantity['ask_quantity'])
                    # print(opp_min_ask_price_quantity['ask_price'])
                else:
                    print("\nCould not find a ask_price or ask_quantity\n")
                    break
                    exch_rate_list.append(0)
            i += 1
        else:
            exch_rate_list.append(0)
        # exch_rate_list.append(((rateB[-1]-rateA[-1])/rateA[-1])*100)  #Expected Profit
        # print("Exchange Rate List: {}".format(exch_rate_list))
        # Compare to determine if Arbitrage opp exists
    try:
        if exch_rate_list[0] != 0 and exch_rate_list[1] != 0 and exch_rate_list[2] != 0:
            if exch_rate_list[0]*exch_rate_list[2]/exch_rate_list[1] > 1:
                # calculate real rate!!!
                exchangeratespread = exch_rate_list[0]*exch_rate_list[2]/exch_rate_list[1] - 1
                opp_exch_rate_list = exch_rate_list
                print(exchangeratespread)
                print("Arbitrage Possibility")
            else:
                # print("No Arbitrage Possibility")
                exchangeratespread = exch_rate_list[0]*exch_rate_list[2]/exch_rate_list[1] - 1
                print(exchangeratespread)
                return None
        else:
            print("One of the exchange rates is 0. No Arbitrage Possibility")
            return None
    except:
        # print("No Arbitrage Possibility")
        return None

    rateA = 0.0  # Original Exchange Rate
    rateB = 0.0  # Calculated/Arbitrage Exchange Rate
    rateB_fee = 0.0  # Include Transaction Fee
    price1 = 0.0  # List for Price of Token (Trade) 1
    price2 = 0.0  # List for price of Token (Trade) 2
    time_list = 0.0  # time of data collection
    profit = 0.0  # Record % profit
    try:
        rateA = (exch_rate_list[0])
        rateB = ((exch_rate_list[1]/exch_rate_list[2]))
        rateB_fee = ((exch_rate_list[1]/exch_rate_list[2])*(1-fee_percentage)*(1-fee_percentage))
        price1 = (exch_rate_list[1])
        price2 = (exch_rate_list[2])
        profit = ((rateA/exch_rate_list[1]) * exch_rate_list[2] - 1) - (fee_percentage * 5)
    except:
        print("One of the rates is 0. Which means minAsk or maxBid returned 0 for ask_price or bid_price respectively. Which prolly means no asks or bids > 100$.")
    if profit > 0 and rateA != 0 and rateB != 0:
        print("FOUND PROFITABLE ARBITRAGE \n")
        print("--------------------------- \n")
        total_fee_pct = fee_percentage * 5
        print("Exchange: {}, Arbitrage: {}, Original Exchange Rate: {}, Arbitrage Exchange Rate: {}, Fee Rate: {}".format(exchange.name, arb_list, rateA, rateB, total_fee_pct))
        print("REAL PROFIT: {} \n".format(profit))
        print("PROFIT IN DOLLARS: {}".format(profit * opp_quantity_list[0] * dollar_exchrate))
        print("INITIAL INVESTMENT AMOUNT IN DOLLARS: {}".format((profit * opp_quantity_list[0] * dollar_exchrate)/profit))
        # var = await exchange.fetch_order_book(symbol=arb_list[0])
        # var1 = await exchange.fetch_order_book(symbol=arb_list[1])
        # var2 = await exchange.fetch_order_book(symbol=arb_list[2])
        # print("HIGHEST BID PRICES (1): {} \n\n".format(var['bids']))
        # print("LOWEST ASK PRICES (2): {} \n\n".format(var1['asks']))
        # print("HIGHEST BID PRICES (3): {}".format(var2['bids']))


        #profit_spread_list.append(profit)
        #profit_volume_list.append()

    #exchange.close()
    arbitrage = {
        'exchange': exchange,
        'sym_list': arb_list,
        'exch_rate_list': opp_exch_rate_list, #maxBid, minAsk, maxBid
        'profit': profit,
        'market_depth_dollars': (profit * opp_quantity_list[0] * dollar_exchrate)/profit,
        'profit_in_dollars': profit * opp_quantity_list[0] * dollar_exchrate,
        'quantity_list': opp_quantity_list,
        'fee_percentage': fee_percentage
    }
    return arbitrage

async def maxBid(exchange, market, total_markets, count, min_USD_for_trade=50):
    orderBook = await requests.get("https://trade.mandala.exchange/open/v1/market/depth?symbol=" + market)
    price_quantity = {}
    finalmarket = ''
    USDTmarket = market[0:3] + "_USDT"
    dollar_exchrate = 0.0
    min_quantity = 0.0
    try:
        USDTorderBook = await requests.get("https://trade.mandala.exchange/open/v1/market/depth?symbol=" + USDTmarket)
        USDTorderBookJson = USDTorderBook.json()
        USDTdepth = USDTorderBookJson['data']
        dollar_exchrate = USDTdepth['bids'][0][0]
        min_quantity = float(min_USD_for_trade/(dollar_exchrate))
    except:
        print('has no bids for USDT')
    try:
        orderBookJson = orderBook.json()
        depth = orderBookJson['data']
        for bid in depth['bids']:
            if bid[1] > min_quantity:
                rounded_bid_price = float(bid[0])
                rounded_bid_quantity = float(bid[1])
                isCorrect = True #setting it to true
                #Not needed
                # ticker = await exchange.fetch_ticker(symbol=market) #SHOULD BE CHANGED
                # average = (ticker['high'] + ticker['low']) / 2 #this as well
                # if (abs(average - rounded_bid_price) < (average * percentUncertaintyOverAverage)):
                #     isCorrect = True
                price_quantity = {
                    'bid_price': rounded_bid_price,
                    'bid_quantity': rounded_bid_quantity,
                    'isFound': isCorrect,
                    'dollar_exchrate': dollar_exchrate
                }
                return price_quantity
        price_quantity = {
            'bid_price': orderBookJson['data']['bids'][0][0],
            'bid_quantity': orderBookJson['data']['bids'][0][1],
            'isFound': False,
            'dollar_exchrate': dollar_exchrate
        }
        print("Could not find a bid above minimum quantity")
        return price_quantity
    except:
        price_quantity = {
            'bid_price': 0,
            'bid_quantity': 0,
            'isFound': False,
            'dollar_exchrate': dollar_exchrate

        }
        print("Error with Max Bid")
        return price_quantity

async def minAsk(exchange, market, total_markets, min_USD_for_trade = 50):
    orderBook = await requests.get("https://trade.mandala.exchange/open/v1/market/depth?symbol=" + market)
    price_quantity = {}
    finalmarket = ''
    min_quantity = 0.0
    USDTmarket = market[0:3] + "_USDT"
    try:
        USDTorderBook = await requests.get("https://trade.mandala.exchange/open/v1/market/depth?symbol=" + USDTmarket)
        USDTorderBookJson = USDTorderBook.json()
        USDTdepth = USDTorderBookJson['data']
        dollar_exchrate = USDTdepth['asks'][0][0]
        min_quantity = float(min_USD_for_trade/(dollar_exchrate))
    except:
        print('has no asks for USDT')
    try:
        orderBookJson = orderBook.json()
        depth = orderBookJson['data']
        for ask in depth['asks']:
            if ask[1] > min_quantity:
                rounded_ask_price = float(ask[0])
                rounded_ask_quantity = float(ask[1])
                isCorrect = True #setting it to true
                #Not needed
                # ticker = await exchange.fetch_ticker(symbol=market) #SHOULD BE CHANGED
                # average = (ticker['high'] + ticker['low']) / 2 #This too
                # if (abs(average - rounded_ask_price) < (average * percentUncertaintyOverAverage)):
                #     isCorrect = True
                price_quantity = {
                    'ask_price': rounded_ask_price,
                    'ask_quantity': rounded_ask_quantity,
                    'isFound': isCorrect
                }
                return price_quantity
        price_quantity = {
            'ask_price': rounded_ask_price,
            'ask_quantity': rounded_ask_quantity,
            'isFound': False
        }
        return price_quantity
    except:
        price_quantity = {
            'ask_price': 0,
            'ask_quantity': 0,
            'isFound': False
        }
        print("Error with minAsk")
        return price_quantity

async def pre_tri_arb_USD_transfer(exchange, sym_list, fee_percentage, initial_quantity): #make exchange, exch_rate_list, sym_list, fee_percentage global vars
    market1 = sym_list[0]
    USDmarket = market1[0:3] + "/BUSD"
    print("Transferring capital in USDC to " + market1)
    try:
        depth = await exchange.fetch_order_book(symbol = USDmarket) #SHOULD BE CHANGED
        USD_sell_exch_rate = round(await maxBid(exchange, market1) ['bid_price']) #is this the highest volume in the bid order book... should it be a limit or market order?
        non_fee_adjusted_quantity = initial_quantity/USD_sell_exch_rate
        totalprice = non_fee_adjusted_quantity * USD_sell_exch_rate
        fee_adjusted_quantity = (totalprice + (totalprice * fee_percentage)) / USD_sell_exch_rate
        if exchange.has['createMarketOrder']: #SHOULD BE CHANGED
            pre_USD_transfer_order = exchange.create_order(symbol=USDmarket, #SHOULD BE CHANGED
                        side=SIDE_SELL,
                        type=ORDER_TYPE_LIMIT,
                        quantity=fee_adjusted_quantity, #compensating for fees so we receive the correct quantity_1
                        price=USD_sell_exch_rate,
                        timeInForce=TIME_IN_FORCE_GTC)
        else:
            print("Could not complete order.")
        checkForOpenOrder(exchange, sym_list[0])
    except:
        print("Market Not Found")

def tri_arb_orders(exchange, exch_rate_list, sym_list, quantity_list, fee_percentage): #exch_rate_list is the exchange rates for the tri arb, sym_list are the 3 markets in the tri arb
    # Place 3 orders in succession buying/selling coins for the tri arb
    print("PLACING ORDER")
    #First Order - Coin 2 from Starting Coin -
    price_order_1 = round(float(exch_rate_list[int(0)]),amount_digits_rounded)
    initial_quantity_traded = quantity_list[0]
    if exchange.has['createMarketOrder']: #SHOULD BE CHANGED
        order_1 = exchange.create_order (symbol=sym_list[0], #SHOULD BE CHANGED
                        side=SIDE_SELL,
                        type=ORDER_TYPE_LIMIT,
                        quantity=initial_quantity_traded,
                        price=price_order_1,
                        timeInForce=TIME_IN_FORCE_GTC)
    else:
        print("Could not complete order.")
    checkForOpenOrder(exchange, sym_list[0])
    #Second Order - Coin 3 from Coin 2 -
    price_order_2 = round(1/exch_rate_list[int(1)], amount_digits_rounded)
    non_fee_adjusted_quantity_2 = initial_quantity_traded/exch_rate_list[0]
    totalprice_1 = non_fee_adjusted_quantity_2 * exch_rate_list[0]
    fee_adjusted_quantity_2 = round((totalprice - (totalprice * fee_percentage)) / exch_rate_list[0], amount_digits_rounded)
    if exchange.has['createMarketOrder']: #SHOULD BE CHANGED
        order_2 = exchange.create_order (symbol=sym_list[1], #SHOULD BE CHANGED
                        side=SIDE_BUY,
                        type=ORDER_TYPE_LIMIT,
                        quantity=fee_adjusted_quantity_2,
                        price=price_order_2,
                        timeInForce=TIME_IN_FORCE_GTC)
    else:
        print("Could not complete order.")
    checkForOpenOrder(exchange, sym_list[1])
    #Third Order - Starting Coin from Coin 3 -
    price_order_3 = round(float(exch_rate_list[int(2)]),amount_digits_rounded)
    non_fee_adjusted_quantity_3 = fee_adjusted_quantity_2/exch_rate_list[1]
    totalprice_2 = non_fee_adjusted_quantity_3 * exch_rate_list[1]
    fee_adjusted_quantity_3 = round((totalprice_2 - (totalprice_2 * fee_percentage)) / exch_rate_list[1], amount_digits_rounded)
    if exchange.has['createMarketOrder']: #SHOULD BE CHANGED
        order_3 = exchange.create_order (symbol=sym_list[2], #SHOULD BE CHANGED
                        side=SIDE_SELL,
                        type=ORDER_TYPE_LIMIT,
                        quantity=fee_adjusted_quantity_3,
                        price=price_order_3,
                        timeInForce=TIME_IN_FORCE_GTC)
    else:
        print("Could not complete order.")
    checkForOpenOrder(exchange, sym_list[2])
    return fee_adjusted_quantity_3

async def post_tri_arb_USD_transfer(exchange,  sym_list, fee_percentage, quantity_3):
    market1 = sym_list[0]
    USDmarket = market1[0:3] + "/USDC"
    print("Transfering capital in " + USDmarket + " to USDC")
    depth = await exchange.fetch_order_book(symbol = USDmarket) #SHOULD BE CHANGED
    USD_buy_exch_rate = round(await minAsk(exchange, market1) ['ask_price'])
    non_fee_adjusted_quantity = quantity_3 / USD_buy_exch_rate
    totalprice = non_fee_adjusted_quantity * USD_buy_exch_rate
    fee_adjusted_quantity = (totalprice - (totalprice * fee_percentage)) / USD_sell_exch_rate
    if exchange.has['createMarketOrder']: #SHOULD BE CHANGED
        post_USD_transfer_order = exchange.create_order(symbol=USDmarket, #SHOULD BE CHANGED
                        side=SIDE_BUY,
                        type=ORDER_TYPE_LIMIT,
                        quantity=quantity_3,
                        price=(1/USD_buy_exch_rate),
                        timeInForce=TIME_IN_FORCE_GTC)
    else:
        print("Could not complete order.")


async def compute_avg_spread(profit_spread_list, profit_dollars_list, market_depth_dollars_list):
    sum_spread = 0
    sum_dollars = 0
    sum_market_depth = 0
    num = 0
    for i in range(0, len(profit_spread_list)):
        sum_spread += profit_spread_list[i]
        try:
            sum_dollars += profit_dollars_list[i]
            sum_market_depth += market_depth_dollars_list[i]
        except:
            pass
        num += 1
    try:
        print("AVERAGE SPREAD: {}".format(sum_spread/num))
        print("AVERAGE PROFIT IN DOLLARS: {}".format(sum_dollars/num))
        print("NUMBER OF TRADES: {}".format(num))
        print("TOTAL PROFIT VOLUME (from this cycle in dollars): {}".format(sum_dollars))
        print("AVERAGE INITIAL INVESTMENT IN DOLLARS (MARKET DEPTH): {}".format(sum_market_depth/num))
    except:
        print("found no profitable spreads!")

def checkForOpenOrder(exchange, market):
    isOpenOrder = True
    check = exchange.fetchOpenOrders(symbol= market) #SHOULD BE CHANGED
    while isOpenOrder:
        if (len(check) == 0):
            isOpenOrder = False
        time.sleep(5)
        check = exchange.fetchOpenOrders(symbol= market) #SHOULD BE CHANGED
        print(check)
    print("Order is Complete")

asyncio.get_event_loop().run_until_complete(run())

if __name__ == "__main__":
    run()
