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
                            # if arb_list[0].split('/')[1] == 'USD':
                            #     final = str(arb_list[1].split('/')[1]) + '/' + arb_list[0].split('/')[1]
                            # else:
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
    quantity_list1 = []
    order_list = []
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


async def find_tri_arb_opp(exchange, total_markets, arb_list, fee_percentage = .001, available_funds_USD = 1000):
    # Determine Rates for our 3 currency pairs - order book
    await exchange.load_markets()
    most_profitable_order = {}
    dollar_exch_ask_list = []
    dollar_exch_bid_list = []
    ask_list = []
    bid_list = []
    ask_list1 = []
    max_dollar_exch_bid = []
    min_dollar_exch_ask =[]
    print("\nChecking for profit: ")
    try:
        orderbook1 = await exchange.fetch_order_book(symbol=arb_list[0])
        orderbook2 = await exchange.fetch_order_book(symbol=arb_list[1])
        orderbook3 = await exchange.fetch_order_book(symbol=arb_list[2])
        min_ask = orderbook1['asks'][0]
        max_bid = orderbook2['bids'][0]
        min_ask = orderbook3['asks'][0]
    except:
        print ("Has no bids or asks for one of the markets OR not loading orderbook")
        return None

    if arb_list[0].split('/')[1] == 'USD':
        #NINAAD START HERE
        spread = await calcSpread3(min_ask, max_bid, min_ask1)
        if spread > 0:
            print("FOUND PROFITABLE ARBITRAGE \n")
            print("--------------------------- \n")
            print("MAXIMUM SPREAD: {}".format(spread))
            print("\n Optimizing for maximum profit volume...")
        else:
            return None
        for bid in orderbook1['bids']:
            if (await calcSpread3(max_dollar_exch_bid, bid, min_ask, min_ask1, min_dollar_exch_ask, fee_percentage)) > 0:
                ask_list.append(bid)
        print("\n bid 1 list: {}".format(ask_list))

        for ask in orderbook2['asks']:
            if (await calcSpread3(max_dollar_exch_bid, min_ask, ask, min_ask1, min_dollar_exch_ask, fee_percentage)) > 0:
                ask_list.append(ask)
        print("\n ask list: {}".format(ask_list))

        for bid in orderbook3['bids']:
            if (await calcSpread3(max_dollar_exch_bid, min_ask, min_ask, bid, min_dollar_exch_ask, fee_percentage)) > 0:
                ask_list1.append(bid)
        print("\n bid 2 list: {}".format(ask_list1))

        for bid in ask_list:
            for ask in ask_list:
                for bid1 in ask_list1:
                    real_spread = await calcSpread3(bid, ask, bid1, fee_percentage)
                    if real_spread > 0:
                        volume, initial_USD, final_USD, calculated_volume = calcVolume3(bid, ask, bid1, real_spread, available_funds_USD)
                        if volume > max_volume:
                            max_volume = volume
                            most_profitable_order['initial_USD'] = volume
                            most_profitable_order['order1'] = [arb_list[0], bid[0], (1/bid[0])*volume]
                            most_profitable_order['order2'] = [arb_list[1], ask[0], (1/bid[0])*volume]
                            most_profitable_order['order3'] = [arb_list[2], bid1[0], ask[0]*(1/bid[0])*volume]
        #NINAAD STOP HERE
    else:
        try:
            usd_market = arb_list[0].split('/')[1] + '/USD'
            usd_orderbook = await exchange.fetch_order_book(symbol=arb_list[0].split('/')[1] + '/USD')
            max_dollar_exch_bid = usd_orderbook['bids'][0]
            min_dollar_exch_ask = usd_orderbook['asks'][0]
        except:
            try:
                usd_market = arb_list[0].split('/')[1] + '/USDC'
                usd_orderbook = await exchange.fetch_order_book(symbol=arb_list[0].split('/')[1] + '/USDC')
                max_dollar_exch_bid = usd_orderbook['bids'][0]
                min_dollar_exch_ask = usd_orderbook['asks'][0]
            except:
                try:
                    usd_market = arb_list[0].split('/')[1] + '/BUSD'
                    usd_orderbook = await exchange.fetch_order_book(symbol=arb_list[0].split('/')[1] + '/BUSD')
                    max_dollar_exch_bid = usd_orderbook['bids'][0]
                    min_dollar_exch_ask = usd_orderbook['asks'][0]
                except:
                    try:
                        usd_market = arb_list[0].split('/')[1] + '/USDT'
                        usd_orderbook = await exchange.fetch_order_book(symbol=arb_list[0].split('/')[1] + '/USDT')
                        max_dollar_exch_bid = usd_orderbook['bids'][0]
                        min_dollar_exch_ask = usd_orderbook['asks'][0]
                    except:
                        try:
                            usd_market = arb_list[0].split('/')[1] + '/USDN'
                            usd_orderbook = await exchange.fetch_order_book(symbol=arb_list[0].split('/')[1] + '/USDN')
                            max_dollar_exch_bid = usd_orderbook['bids'][0]
                            min_dollar_exch_ask = usd_orderbook['asks'][0]
                        except:
                            print("Could not find compatible USD market for starting coin :(")
                            return None

        spread = await calcSpread5(max_dollar_exch_bid, max_bid, min_ask, max_bid1, min_dollar_exch_ask, fee_percentage)

        if spread > 0:
            print("FOUND PROFITABLE ARBITRAGE \n")
            print("--------------------------- \n")
            print("Exchange: {}, Arbitrage: {}".format(exchange.id, arb_list))
            print("MAXIMUM SPREAD: {}".format(spread))
            print("\nOptimizing for maximum profit volume...")
        else:
            return None

        for bid in usd_orderbook['bids']:
            if (await calcSpread5(bid, max_bid, min_ask, max_bid1, min_dollar_exch_ask, fee_percentage)) > 0:
                dollar_exch_ask_list.append(bid)
        print("\ndollar bid list: {}".format(dollar_exch_ask_list))

        for bid in orderbook1['bids']:
            if (await calcSpread5(max_dollar_exch_bid, bid, min_ask, max_bid1, min_dollar_exch_ask, fee_percentage)) > 0:
                ask_list.append(bid)
        print("\n bid 1 list: {}".format(ask_list))

        for ask in orderbook2['asks']:
            if (await calcSpread5(max_dollar_exch_bid, max_bid, ask, max_bid1, min_dollar_exch_ask, fee_percentage)) > 0:
                ask_list.append(ask)
        print("\n ask list: {}".format(ask_list))

        for bid in orderbook3['bids']:
            if (await calcSpread5(max_dollar_exch_bid, max_bid, min_ask, bid, min_dollar_exch_ask, fee_percentage)) > 0:
                ask_list1.append(bid)
        print("\n bid 2 list: {}".format(ask_list1))

        for ask in usd_orderbook['asks']:
            if (await calcSpread5(max_dollar_exch_bid, max_bid, min_ask, max_bid1, ask, fee_percentage)) > 0:
                dollar_exch_ask_list.append(ask)
        print("\ndollar ask list: {}".format(dollar_exch_ask_list))

        max_volume = 0.0
        real_spread = 0.0
        for dollar_bid in dollar_exch_ask_list:
            for bid in ask_list:
                for ask in ask_list:
                    for bid1 in ask_list1:
                        for dollar_ask in dollar_exch_ask_list:
                            real_spread = await calcSpread5(dollar_bid, bid, ask, bid1, dollar_ask, fee_percentage)
                            if real_spread > 0:
                                volume, initial_USD, final_USD, calculated_volume = await calcVolume5(dollar_bid, bid, ask, bid1, dollar_ask, real_spread, available_funds_USD, fee_percentage)
                                if volume > max_volume:
                                    max_volume = volume
                                    most_profitable_order['initial_USD'] = volume
                                    most_profitable_order['order1'] = [usd_market, dollar_bid[0], (1/dollar_bid[0])*volume]
                                    most_profitable_order['order2'] = [arb_list[0], bid[0], (1/bid[0])*(1/dollar_bid[0])*volume]
                                    most_profitable_order['order3'] = [arb_list[1], ask[0], (1/bid[0])*(1/dollar_bid[0])*volume]
                                    most_profitable_order['order4'] = [arb_list[2], bid1[0], ask[0]*(1/bid[0])*(1/dollar_bid[0])*volume]
                                    most_profitable_order['order5'] = [usd_market, dollar_ask[0], ask[0]*(1/bid[0])*(1/dollar_bid[0])*volume]
        print("TRADE WITH MAXIMUM VOLUME: volume in USD: {}, order: {}".format(max_volume, most_profitable_order))
    arbitrage = {
        'exchange': exchange,
        'sym_list': arb_list,
        'profit': real_spread,
        'profit_in_dollars': real_spread * most_profitable_order['initial_USD'],
        'fee_percentage': fee_percentage
    }
    return arbitrage


async def calcVolume5(dollar_exch_bid, bid, ask, bid1, dollar_exch_ask, spread, available_funds_USD, fee_percentage):
    print("SPREAD1111: {}".format(spread))
    initial_USD = dollar_exch_bid[0] * dollar_exch_bid[1]
    if initial_USD > available_funds_USD:
        initial_USD = available_funds_USD
    quantity_coin1 = (1-fee_percentage) * initial_USD * (1/dollar_exch_bid[0])
    if (1/bid[0]) * quantity_coin1 > bid[1]:
        quantity_coin1 = bid[0] * bid[1]
        initial_USD = quantity_coin1 * dollar_exch_bid[0]
    quantity_coin2 = bid[1]
    if quantity_coin2 > ask[1]:
        quantity_coin2 = ask[1]
        quantity_coin1 = bid[0] * quantity_coin2
        initial_USD = quantity_coin1 * dollar_exch_bid[0]
    quantity_coin3 = ask[0] * quantity_coin2
    if (1/bid1[0]) * quantity_coin3 > bid1[1]:
        quantity_coin3 = bid1[0] * bid1[1]
        quantity_coin2 = quantity_coin3 * (1/ask[0])
        quantity_coin1 = bid[0] * quantity_coin2
        initial_USD = quantity_coin1 * dollar_exch_bid[0]
    quantity_coin1_final = bid1[1]
    if quantity_coin1_final > dollar_exch_ask[1]:
        quantity_coin1_final = dollar_exch_ask[1]
        quantity_coin3 = bid1[0] * quantity_coin1_final
        quantity_coin2 = quantity_coin3 * (1/ask[0])
        quantity_coin1 = bid[0] * quantity_coin2
        initial_USD = quantity_coin1 * dollar_exch_bid[0]
    final_USD = dollar_exch_ask[0] * quantity_coin1_final
    print("\nINITIAL USD INVESTMENT: {}".format(initial_USD))
    print("FINAL USD AMOUNT: {}".format(final_USD))
    print("CALCULATED VOLUME: {}".format(final_USD - initial_USD))
    print("THEORETICAL VOLUME: {}".format(initial_USD * spread))
    return initial_USD * spread, initial_USD, final_USD, final_USD - initial_USD


async def calcVolume3(bid, ask, bid1, spread, available_funds_USD):
    quantity_coin1 = available_funds_USD
    if (1/bid[0]) * quantity_coin1 > bid[1]:
        quantity_coin1 = bid[0] * bid[1]
        initial_USD = quantity_coin1 * dollar_exch_bid[0]
    quantity_coin2 = bid[1]
    if quantity_coin2 > ask[1]:
        quantity_coin2 = ask[1]
        quantity_coin1 = bid[0] * quantity_coin2
        initial_USD = quantity_coin1 * dollar_exch_bid[0]
    quantity_coin3 = ask[0] * quantity_coin2
    if (1/bid1[0]) * quantity_coin3 > bid1[1]:
        quantity_coin3 = bid1[0] * bid1[1]
        quantity_coin2 = quantity_coin3 * (1/ask[0])
        quantity_coin1 = bid[0] * quantity_coin2
        initial_USD = quantity_coin1 * dollar_exch_bid[0]
    quantity_coin1_final = bid1[1]
    return quantity_coin1 * spread, quantity_coin1, quantity_coin1_final, quantity_coin1_final - quantity_coin1


async def calcSpread5(dollar_exch_bid, bid, ask, bid1, dollar_exch_ask, fee_percentage):
    # return ((dollar_exch_bid[0]) * (1/bid[0]) * (ask[0]) * (1/bid1[0]) * (1/dollar_exch_ask[0]) - 1) - (fee_percentage * 5)
    arbitrage_spread = (1/bid[0]) * (ask[0]) * (1/bid1[0]) - 1 - (fee_percentage * 5)
    adjusted_spread = ((1/dollar_exch_bid[0]) * (1/bid[0]) * (ask[0]) * (1/bid1[0]) * (dollar_exch_ask[0]) - 1) - (fee_percentage * 5)
    print("ARBITRAGE SPREAD: {}".format(arbitrage_spread))
    print("SPREAD: {}".format(adjusted_spread))
    return adjusted_spread

async def calcSpread3(bid, ask, bid1, fee_percentage):
    #NINAAD CHANGE THIS FUNCTION
    return (1/bid[0]) * ask[0] * (1/bid1[0]) - (fee_percentage * 3)


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