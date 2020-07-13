import ccxtpro
import ccxt
import datetime
import time
import random
from pprint import pprint
import asyncio

transfer_symbol = 'USDC'
amount_digits_rounded = 5
percentUncertaintyOverAverage = .3

async def run():
    # exchange = ccxt.binance()
    # await exchange.load_markets()
    # test = exchange.symbols
    # print(test)

    list_of_lists_of_arb_lists = await config_arbitrages()
    while 1:
        profit_spread_list, profit_dollars_list, quantity_list = await execute_all_tri_arb_orders(list_of_lists_of_arb_lists)
        await compute_avg_spread(profit_spread_list, profit_dollars_list, quantity_list)
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
    for exch in ccxtpro.exchanges:  # initialize Exchange
        # filtered_exchanges = [ 'binance', 'coinbase' 'bequant', 'binanceje', 'binanceus', 'bitfinex', 'bitmex', 'bitstamp', 'bittrex', 'bitvavo', 'coinbaseprime', 'coinbasepro', 'ftx', 'gateio', 'hitbtc', 'huobijp',
        #                         'huobipro', 'huobiru', 'kraken', 'kucoin', 'okcoin', 'okex', 'phemex', 'poloniex', 'upbit']
        filtered_exchanges = ['binanceus']
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
            val = await exchange1.load_markets()
            markets = val.keys()
            # pprint(await exchange1.fetch_order_book(symbol='BTC/USD'))
        except:
            print('\nExchange is not loading markets.. Moving on\n')
            continue
        print("Exchange Name: {}".format(exchange1.id))
        # print(symbols)
        symbols = exchange1.symbols
        if symbols is None:
            print("Skipping Exchange ", exch)
            print("\n-----------------\nNext Exchange\n-----------------")
            continue
        elif len(symbols) < 30:
            print("\n-----------------\nNeed more Pairs (Next Exchange)\n-----------------")
            continue
        else:
            print(exchange1)
            exchange1_info = dir(exchange1)
            print("------------Exchange: ", exchange1.id)
            print(exchange1.symbols)  # List all currencies
            # time.sleep(5)

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
                    # print(arb_list[2])
                    if arb_list[2] in exchange1.symbols:
                        # print(arb_list)
                        list_of_arb_lists.append(arb_list)

            print("\nList of Arbitrage Symbols:", list_of_arb_lists)
            list_of_lists_of_arb_lists.append([exchange1, list_of_arb_lists, markets])
    return list_of_lists_of_arb_lists



async def execute_all_tri_arb_orders(list_of_lists_of_arb_lists):
    #Determines profitability and executes profitable orders.
    profit_spread_list = []
    profit_dollars_list = []
    quantity_list1 =[]
    for list_of_arb_lists in list_of_lists_of_arb_lists:
        exchange = list_of_arb_lists[0]
        markets = list_of_arb_lists[2]
        for arb_list in list_of_arb_lists[1]:
            arbitrageopp = await find_tri_arb_opp(exchange, markets, arb_list)
            try:
                if(arbitrageopp['profit'] > 0.0):
                    profit_spread_list.append(arbitrageopp['profit'])
                    quantity_list1.append([arbitrageopp['sym_list'][0], arbitrageopp['quantity_list'][0]])
                    profit_dollars_list.append(arbitrageopp['profit_in_dollars'])
                    quantity_list = arbitrageopp['quantity_list']
                    # await pre_tri_arb_USD_transfer(arbitrageopp['exchange'], arbitrageopp['sym_list'], arbitrageopp['fee_percentage'], quantity_list[0])
                    # quantity_3 = tri_arb_orders(arbitrageopp['exchange'], arbitrageopp['exch_rate_list'], arbitrageopp['sym_list'], arbitrageopp['quantity_list'], arbitrageopp['fee_percentage'])
                    # await post_tri_arb_USD_transfer(arbitrageopp['exchange'],  arbitrageopp['sym_list'], arbitrageopp['fee_percentage'], quantity_3)
                    print("\nOrdering should be complete by this point\n")
            except:
                print("\n\nNo Arbitrage Possibility\n\n")
    return profit_spread_list, profit_dollars_list, quantity_list1


async def find_tri_arb_opp(exchange, total_markets, arb_list, fee_percentage = .001):
    # Determine Rates for our 3 currency pairs - order book
    await exchange.load_markets()
    opp_exch_rate_list = []
    opp_quantity_list = []
    opp_max_bid_price_quantity = []
    list_exch_rate_list = []
    exch_rate_list = []
    bid1_list = []
    ask_list = []
    bid2_list = []
    dollar_exchrate = 0.0
    i = 0
    count = 0
    print("\nChecking for profit: ")
    for sym in arb_list:
        # print(sym)
        if sym in exchange.symbols:
            if i % 2 == 0:
                opp_max_bid_price_quantity = await maxBid(exchange, sym, total_markets, count)
                if opp_max_bid_price_quantity['isFound']:
                    exch_rate_list.append(opp_max_bid_price_quantity['bid_price'])
                    opp_quantity_list.append(opp_max_bid_price_quantity['bid_quantity'])
                    bid1_list.append([opp_max_bid_price_quantity['bid_price'],opp_max_bid_price_quantity['bid_quantity']])
                    if count == 0:
                        dollar_exchrate = opp_max_bid_price_quantity['dollar_exchrate']
                else:
                    print("\nCould not find a bid_price or bid_quantity\n")
                    break
                    exch_rate_list.append(0)
                count += 1
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
            if (1/exch_rate_list[0])*exch_rate_list[1]/exch_rate_list[2] > 1:
                # calculate real rate!!!
                exchangeratespread = (1/exch_rate_list[0])*exch_rate_list[1]/exch_rate_list[2] - 1
                opp_exch_rate_list = exch_rate_list
                print(exchangeratespread)
                print("Arbitrage Possibility")
            else:
                # print("No Arbitrage Possibility")
                exchangeratespread = (1/exch_rate_list[0])*exch_rate_list[1]/exch_rate_list[2] - 1
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
        rateB = (exch_rate_list[1]/exch_rate_list[2])
        rateB_fee = ((exch_rate_list[1]/exch_rate_list[2])*(1-fee_percentage)*(1-fee_percentage))
        price1 = (exch_rate_list[1])
        price2 = (exch_rate_list[2])
        profit = ((1/exch_rate_list[0])*exch_rate_list[1]/exch_rate_list[2] - 1) - (fee_percentage * 5)
    except:
        print("One of the rates is 0. Which means minAsk or maxBid returned 0 for ask_price or bid_price respectively. Which prolly means no asks or bids > 100$.")
    if profit > 0 and rateA != 0 and rateB != 0:
        print("FOUND PROFITABLE ARBITRAGE \n")
        print("--------------------------- \n")
        total_fee_pct = fee_percentage * 5
        print("Exchange: {}, Arbitrage: {}, Original Exchange Rate: {}, Arbitrage Exchange Rate: {}, Fee Rate: {}".format(exchange.id, arb_list, rateA, rateB, total_fee_pct))
        print("REAL PROFIT (BEST CASE SCENARIO): {}".format(profit))
        print("QUANTITY OF STARTING COIN: {} \n".format(exch_rate_list[0]*opp_quantity_list[0]))
        # print("PROFIT IN DOLLARS: {}".format(profit * opp_quantity_list[0] * dollar_exchrate))
        # var = await exchange.fetch_order_book(symbol=arb_list[0])
        # var1 = await exchange.fetch_order_book(symbol=arb_list[1])
        # var2 = await exchange.fetch_order_book(symbol=arb_list[2])
        # print("HIGHEST BID PRICES (1): {} \n\n".format(var['bids']))
        # print("HIGHEST ASK PRICES (2): {} \n\n".format(var1['asks']))
        # print("HIGHEST BID PRICES (3): {}".format(var2['bids']))


        #profit_spread_list.append(profit)
        #profit_volume_list.append()

    #
    arbitrage = {
        'exchange': exchange,
        'sym_list': arb_list,
        'exch_rate_list': opp_exch_rate_list, #maxBid, minAsk, maxBid
        'profit': profit,
        'profit_in_dollars': profit * opp_quantity_list[0] * dollar_exchrate,
        'quantity_list': opp_quantity_list,
        'fee_percentage': fee_percentage
    }
    return arbitrage

async def maxBid(exchange, market, total_markets, count, min_USD_for_trade=1000):
    try:
        dollar_exchrate = 0.0
        await exchange.load_markets()
        # if count == 0:
        #     USDmarket = market[0:3] + "/USD"
        #     USDCmarket = market[0:3] + "/USDC"
        #     USDTmarket = market[0:3] + "/USDT"
        #     if USDmarket in exchange.symbols:
        #         USDdepth = await exchange.fetch_order_book(symbol=USDmarket)
        #         dollar_exchrate = USDdepth['bids'][0][0]
        #     elif USDCmarket in exchange.symbols:
        #         USDCdepth = await exchange.fetch_order_book(symbol=USDCmarket)
        #         dollar_exchrate = USDCdepth['bids'][0][0]
        #     elif USDTmarket in exchange.symbols:
        #         USDTdepth = await exchange.fetch_order_book(symbol=USDTmarket)
        #         dollar_exchrate = USDTdepth['bids'][0][0]
        
        depth = await exchange.fetch_order_book(symbol=market)
        # print(depth)
        price_quantity = {
            'bid_price': depth['bids'][0][0],
            'bid_quantity': depth['bids'][0][1],
            'isFound': True,
            'dollar_exchrate': dollar_exchrate
        }
    except:
        price_quantity = {
            'bid_price': 0,
            'bid_quantity': 0,
            'isFound': False,
            'dollar_exchrate': 0
        }
    return price_quantity

async def minAsk(exchange, market, total_markets, min_USD_for_trade = 1000):
    try:
        await exchange.load_markets()
        depth = await exchange.fetch_order_book(symbol=market)
        price_quantity = {
            'ask_price': depth['asks'][0][0],
            'ask_quantity': depth['asks'][1][0],
            'isFound': True
        }
    except:
        price_quantity = {
            'ask_price': 0,
            'ask_quantity': 0,
            'isFound': False
        }
    return price_quantity

async def pre_tri_arb_USD_transfer(exchange, sym_list, fee_percentage, initial_quantity): #make exchange, exch_rate_list, sym_list, fee_percentage global vars
    market1 = sym_list[0]
    USDmarket = market1[0:3] + "/USDC"
    print("Transferring capital in USDC to " + market1)
    try:
        depth = await exchange.fetch_order_book(symbol = USDmarket)
        USD_sell_exch_rate = round(await maxBid(exchange, market1) ['bid_price']) #is this the highest volume in the bid order book... should it be a limit or market order?
        non_fee_adjusted_quantity = initial_quantity/USD_sell_exch_rate
        totalprice = non_fee_adjusted_quantity * USD_sell_exch_rate
        fee_adjusted_quantity = (totalprice + (totalprice * fee_percentage)) / USD_sell_exch_rate
        if exchange.has['createMarketOrder']:
            pre_USD_transfer_order = exchange.create_order(symbol=USDmarket,
                        side=SIDE_SELL,
                        type=ORDER_TYPE_LIMIT,
                        quantity=fee_adjusted_quantity, #compensating for fees so we receive the correct quantity_1
                        price=USD_sell_exch_rate,
                        timeInForce=TIME_IN_FORCE_GTC)
        else:
            print("Could not complete order.")
        print("Pre Tri Arb Coin Transfer Complete")
    except:
        print("Market Not Found")

def tri_arb_orders(exchange, exch_rate_list, sym_list, quantity_list, fee_percentage): #exch_rate_list is the exchange rates for the tri arb, sym_list are the 3 markets in the tri arb
    # Place 3 orders in succession buying/selling coins for the tri arb
    print("PLACING ORDER")
    # Round Coin Amounts of Binance Coin (must be purchased in whole amounts)
    # for a, sym in enumerate(sym_list):
    #     print(sym)
    #     if sym[0:3]=='BNB' or sym[-3:]=='BNB':
    #         coin_amts[a+1] = math.ceil(coin_amts[a+1])
    #         print(coin_amts[a])
    # real_order_start_time = datetime.now()
    # real_order_msg1+="\nSTART TIME: " + str(real_order_start_time)+"\n\n"
    #First Order - Coin 2 from Starting Coin -
    price_order_1 = round(float(exch_rate_list[int(0)]),amount_digits_rounded)
    initial_quantity_traded = quantity_list[0]
    if exchange.has['createMarketOrder']:
        order_1 = exchange.create_order (symbol=sym_list[0],
                        side=SIDE_SELL,
                        type=ORDER_TYPE_LIMIT,
                        quantity=initial_quantity_traded,
                        price=price_order_1,
                        timeInForce=TIME_IN_FORCE_GTC)
    else:
        print("Could not complete order.")
    print('Tri Arb Order 1 Complete')
    #Second Order - Coin 3 from Coin 2 -
    price_order_2 = round(1/exch_rate_list[int(1)], amount_digits_rounded)
    non_fee_adjusted_quantity_2 = initial_quantity_traded/exch_rate_list[0]
    totalprice_1 = non_fee_adjusted_quantity_2 * exch_rate_list[0]
    fee_adjusted_quantity_2 = round((totalprice - (totalprice * fee_percentage)) / exch_rate_list[0], amount_digits_rounded)
    if exchange.has['createMarketOrder']:
        order_2 = exchange.create_order (symbol=sym_list[1],
                        side=SIDE_BUY,
                        type=ORDER_TYPE_LIMIT,
                        quantity=fee_adjusted_quantity_2,
                        price=price_order_2,
                        timeInForce=TIME_IN_FORCE_GTC)
    else:
        print("Could not complete order.")
    #Third Order - Starting Coin from Coin 3 -
    price_order_3 = round(float(exch_rate_list[int(2)]),amount_digits_rounded)
    non_fee_adjusted_quantity_3 = fee_adjusted_quantity_2/exch_rate_list[1]
    totalprice_2 = non_fee_adjusted_quantity_3 * exch_rate_list[1]
    fee_adjusted_quantity_3 = round((totalprice_2 - (totalprice_2 * fee_percentage)) / exch_rate_list[1], amount_digits_rounded)
    if exchange.has['createMarketOrder']:
        order_3 = exchange.create_order (symbol=sym_list[2],
                        side=SIDE_SELL,
                        type=ORDER_TYPE_LIMIT,
                        quantity=fee_adjusted_quantity_3,
                        price=price_order_3,
                        timeInForce=TIME_IN_FORCE_GTC)
    else:
        print("Could not complete order.")
    return fee_adjusted_quantity_3

async def post_tri_arb_USD_transfer(exchange,  sym_list, fee_percentage, quantity_3):
    market1 = sym_list[0]
    USDmarket = market1[0:3] + "/USDC"
    print("Transfering capital in " + USDmarket + " to USDC")
    depth = await exchange.fetch_order_book(symbol = USDmarket)
    USD_buy_exch_rate = round(await minAsk(exchange, market1) ['ask_price'])
    non_fee_adjusted_quantity = quantity_3 / USD_buy_exch_rate
    totalprice = non_fee_adjusted_quantity * USD_buy_exch_rate
    fee_adjusted_quantity = (totalprice - (totalprice * fee_percentage)) / USD_sell_exch_rate
    if exchange.has['createMarketOrder']:
        post_USD_transfer_order = exchange.create_order(symbol=USDmarket,
                        side=SIDE_BUY,
                        type=ORDER_TYPE_LIMIT,
                        quantity=quantity_3,
                        price=(1/USD_buy_exch_rate),
                        timeInForce=TIME_IN_FORCE_GTC)
    else:
        print("Could not complete order.")


async def compute_avg_spread(profit_spread_list, profit_dollars_list, quantity_list):
    sum_spread = 0
    sum_dollars = 0
    num = 0

    for i in range(0, len(profit_spread_list)):
        sum_spread += profit_spread_list[i]
        sum_dollars += profit_dollars_list[i]
        print("MARKET: {}".format(quantity_list[i][0]))
        print("INITIAL QUANTITY OF STARTING COIN: {}".format(quantity_list[i][1]))
        print("SPREAD: {}".format(profit_spread_list[i]))
        print("PROFIT IN TERMS OF STARTING COIN:{}".format(profit_spread_list[i]*quantity_list[i][1]))
        num += 1
    try:
        print("AVERAGE SPREAD: {}".format(sum_spread/num))
        print("AVERAGE PROFIT IN DOLLARS: {}".format(sum_dollars/num))
        print("NUMBER OF TRADES: {}".format(num))
        print("TOTAL PROFIT VOLUME (from this cycle in dollars): {}".format(sum_dollars))
    except:
        print("found no profitable spreads!")



asyncio.get_event_loop().run_until_complete(run())

if __name__ == "__main__":
    run()