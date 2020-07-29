import ccxtpro
import ccxt
import datetime
import time
import csv
import random
from pprint import pprint
import asyncio

with open('triarbdata.csv', 'w') as f:
    fieldnames = ['Bot Start Date', 'Bot Start Time', 'Exchange', 'Initial USD', 'First Market', 'Second Market', 'Third Market', 'Spread', 'Estimated Profit']
    thewriter = csv.DictWriter(f, fieldnames = fieldnames)
    thewriter.writeheader()
    current_time = datetime.datetime.now()

    transfer_symbol = 'USDC'
    amount_digits_rounded = 5
    percentUncertaintyOverAverage = .3
    fee_pcts = {
        'binanceus': .001,
        'kraken': .0026,
        'bittrex': .005
    }

    async def run():
        # exchange = ccxt.binance()
        # await exchange.load_markets()
        # test = exchange.symbols
        # print(test)

        list_of_lists_of_arb_lists = await config_arbitrages()
        while 1:
            await execute_all_tri_arb_orders(list_of_lists_of_arb_lists)
            # await compute_avg_spread(profit_spread_list, profit_dollars_list, quantity_list)
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
            print("CYCLE FINISHED, STARTING NEXT CYCLE...")
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
            filtered_exchanges = ['kraken', 'bittrex']
            if exch not in filtered_exchanges:
                continue
            if exch == 'binanceus':
                exchange1 = getattr(ccxtpro, 'binanceus')({
                    'apiKey': 'W6fJUrx0LLcrdNE1GJ9B5yK0NRPMhhWjDtotxrdI3FirqUlBIzNHtWdza0TLn2Sy',
                    'secret': 'TIAIQHixpiIeUOXRaf3joBVJP9rHizsEcALDuadL1VAeZCsPMem3KtxRfWMYZth9',
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
            elif exch == 'kraken':
                exchange1 = getattr(ccxtpro, 'kraken')({
                    'apiKey': '23c833b7f0474c26b6367081904b9083',
                    'secret': 'f8cd636f627d4680b28a01af8b48cfca',
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
                print(exchange1.symbols)


                list_of_arb_lists = []
                list_of_arb_listswmarkets = []
                for symb in symbols:
                    arb_list = [symb]
                    j = 0
                    while 1:
                        if j >= 1:
                            if len(arb_list) > 1:
                                final = arb_list[0].split('/')[1] + '/' + str(arb_list[1].split('/')[1])
                                # print(final)
                                if final in exchange1.symbols:
                                    arb_list.append(final)
                                # elif arb_list[1].split('/')[1] + '/' + str(arb_list[0].split('/')[1]) in exchange1.symbols:
                                #     arb_list.append(arb_list[1].split('/')[1] + '/' + str(arb_list[0].split('/')[1]))
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
                        # print(arb_list[2])
                        if arb_list[2] in exchange1.symbols:
                            # print(arb_list)
                            list_of_arb_lists.append(arb_list)

                print("\nList of Arbitrage Symbols:", list_of_arb_lists)
                list_of_lists_of_arb_lists.append([exchange1, list_of_arb_lists, markets])
        return list_of_lists_of_arb_lists



    async def execute_all_tri_arb_orders(list_of_lists_of_arb_lists):
        #Determines profitability and executes profitable orders.
        cpu = 0
        profit_spread_list = []
        quantity_list1 =[]
        for list_of_arb_lists in list_of_lists_of_arb_lists:
            exchange = list_of_arb_lists[0]
            markets = list_of_arb_lists[2]
            arbitrageopp = 0
            for arb_list in list_of_arb_lists[1]:
                if arb_list[0].split('/')[1] not in ['USD', 'USDT', 'BUSD']:
                    arbitrageopp = await find_tri_arb_opp1(exchange, markets, arb_list)
                else:
                    arbitrageopp = await find_tri_arb_opp1_USD(exchange, markets, arb_list)
                try:
                    if(arbitrageopp['profit'] > 0.0):
                        # if arbitrageopp['sym_list'][0].split('/')[1] not in ['USDT', 'BUSD']:
                        profit_spread_list.append(arbitrageopp['spread'])
                        quantity_list1.append([arbitrageopp['sym_list'][0], arbitrageopp['quantity_list'][0]])
                        quantity_list = arbitrageopp['quantity_list']
                        writeToCSV(arbitrageopp)

                        # await create_order(exchange, arbitrageopp)

                        # await pre_tri_arb_USD_transfer(arbitrageopp['exchange'], arbitrageopp['sym_list'], arbitrageopp['fee_percentage'], quantity_list[0])
                        # quantity_3 = tri_arb_orders(arbitrageopp['exchange'], arbitrageopp['exch_rate_list'], arbitrageopp['sym_list'], arbitrageopp['quantity_list'], arbitrageopp['fee_percentage'])
                        # await post_tri_arb_USD_transfer(arbitrageopp['exchange'],  arbitrageopp['sym_list'], arbitrageopp['fee_percentage'], quantity_list[2])
                        print("\nOrdering should be complete by this point\n")
                except Exception as inst:
                    print(type(inst))
                    print(inst)
                    print("\n\nNo Arbitrage Possibility\n\n")
        return profit_spread_list, quantity_list1


    #creates order for an arbitrage opportunity (limit order strategy)
    async def create_order(exchange, arbitrageopp):
        await exchange.load_markets()
        if exchange.has['fetchOpenOrders']:
            # open_orders = await exchange.fetch_open_orders()
            if 1: #len(open_orders) == 0:
                if len(arbitrageopp['exch_rate_list']) > 3:
                    try:
                        await exchange.create_limit_buy_order(arbitrageopp['sym_list'][0].split('/')[1] + '/' + 'USD', arbitrageopp['quantity_list'][0], arbitrageopp['exch_rate_list'][0])
                        while 1:
                            open_orders = await exchange.fetch_open_orders(symbol=arbitrageopp['sym_list'][0].split('/')[1] + '/' + 'USD')
                            if len(open_orders) > 0:
                                time.sleep(120)
                                continue
                            break
                        await exchange.create_limit_buy_order(arbitrageopp['sym_list'][0], arbitrageopp['quantity_list'][2], arbitrageopp['exch_rate_list'][1])
                        while 1:
                            open_orders = await exchange.fetch_open_orders(symbol=arbitrageopp['sym_list'][0])
                            if len(open_orders) > 0:
                                time.sleep(120)
                                continue
                            break
                        await exchange.create_limit_sell_order(arbitrageopp['sym_list'][1], arbitrageopp['quantity_list'][2], arbitrageopp['exch_rate_list'][2])
                        while 1:
                            open_orders = await exchange.fetch_open_orders(symbol=arbitrageopp['sym_list'][1])
                            if len(open_orders) > 0:
                                time.sleep(120)
                                continue
                            break
                        await exchange.create_limit_buy_order(arbitrageopp['sym_list'][2], arbitrageopp['quantity_list'][4], arbitrageopp['exch_rate_list'][3])
                        while 1:
                            open_orders = await exchange.fetch_open_orders(symbol=arbitrageopp['sym_list'][2])
                            if len(open_orders) > 0:
                                time.sleep(120)
                                continue
                            break
                        await exchange.create_limit_sell_order(arbitrageopp['sym_list'][0].split('/')[1] + '/' + 'USD', arbitrageopp['quantity_list'][4], arbitrageopp['exch_rate_list'][4])
                        while 1:
                            open_orders = await exchange.fetch_open_orders(symbol=arbitrageopp['sym_list'][0].split('/')[1] + '/' + 'USD')
                            if len(open_orders) > 0:
                                time.sleep(120)
                                continue
                            break
                        print('ORDER COMPLETED! :) YESSIRRR LETS GET THIS BREAD')
                    except Exception as inst:
                        print("ERROR: SOMETHING WENT WRONG WITH ORDER")
                        print("ERROR TYPE: {}".format(type(inst)))
                        print("ERROR: {}".format(inst))
                else:
                    try:
                        await exchange.create_limit_buy_order(arbitrageopp['sym_list'][0], arbitrageopp['quantity_list'][1], arbitrageopp['exch_rate_list'][0])
                        while 1:
                            open_orders = await exchange.fetch_open_orders(symbol=arbitrageopp['sym_list'][0])
                            if len(open_orders) > 0:
                                time.sleep(40)
                                continue
                            break
                        balances = await exchange.fetch_balance()
                        await exchange.create_limit_sell_order(arbitrageopp['sym_list'][1], balances['free'][arbitrageopp['sym_list'][0].split('/')[0]], arbitrageopp['exch_rate_list'][1])
                        while 1:
                            open_orders = await exchange.fetch_open_orders(symbol=arbitrageopp['sym_list'][1])
                            if len(open_orders) > 0:
                                time.sleep(40)
                                continue
                            break
                        balances = await exchange.fetch_balance()
                        if arbitrageopp['sym_list'][1].split('/')[1] != 'USD':
                            await exchange.create_limit_buy_order(arbitrageopp['sym_list'][2], balances['free'][arbitrageopp['sym_list'][1].split('/')[1]], arbitrageopp['exch_rate_list'][2])
                            while 1:
                                open_orders = await exchange.fetch_open_orders(symbol=arbitrageopp['sym_list'][2])
                                if len(open_orders) > 0:
                                    time.sleep(40)
                                    continue
                                break
                        print('ORDER COMPLETED! :) YESSIRRR LETS GET THIS BREAD')
                    except Exception as inst:
                        print("ERROR: SOMETHING WENT WRONG WITH ORDER")
                        print("ERROR TYPE: {}".format(type(inst)))
                        print("ERROR: {}".format(inst))
            else:
                print("ANOTHER ORDER IN PROGRESS")
                return
        else:
            print("CANNOT CHECK IF OPEN ORDERS PRESENT")
            return



    async def find_tri_arb_opp1(exchange, total_markets, arb_list, fee_percentage = .001):
        # Determine Rates for our 3 currency pairs - order book
        await exchange.load_markets()
        fee_percentage = fee_pcts[exchange.id]
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
        print(arb_list)
        try:
            orderbook1 = await exchange.fetch_order_book(symbol=arb_list[0])
            orderbook2 = await exchange.fetch_order_book(symbol=arb_list[1])
            orderbook3 = await exchange.fetch_order_book(symbol=arb_list[2])
            max_bid = orderbook1['bids'][0]
            min_ask = orderbook2['asks'][0]
            max_bid1 = orderbook3['bids'][0]
        except:
            print ("Has no bids or asks for one of the markets OR not loading orderbook")
            return None
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
                            # if arb_list[0].split('/')[1] != 'USD'
                            return None
        spread = (1/max_dollar_exch_bid[0]) * ((1/max_bid[0]) * min_ask[0] * (1/max_bid1[0])) * min_dollar_exch_ask[0] - 1
        print(spread)
        fee_adjusted_spread = spread - (fee_percentage*5)
        #depths = await findLowestDepth(max_dollar_exch_bid, max_bid, min_ask, max_bid1, min_dollar_exch_ask, fee_adjusted_spread, (await exchange.fetch_balance())['free'][usd_market.split('/')[1]], fee_pcts[exchange.id])# (await exchange.fetch_balance())['free'][arb_list[1].split('/')[1]])
        depths = await findLowestDepth(max_dollar_exch_bid, max_bid, min_ask, max_bid1, min_dollar_exch_ask, fee_adjusted_spread, 10000, fee_pcts[exchange.id])
        if spread > 0:
            if (depths['final_USD'] - depths['initial_USD'])/depths['initial_USD'] > 0:
                print("FOUND PROFITABLE ARBITRAGE \n")
                print("--------------------------- \n")
                print("Exchange: {}, Arbitrage: {}".format(exchange.id, arb_list))
                print("REAL PROFIT (BEST CASE SCENARIO): {}".format((depths['final_USD'] - depths['initial_USD'])/depths['initial_USD']))
                print("QUANTITY OF STARTING COIN (BEST CASE): {} \n".format(max_bid[0] * max_bid[1]))
                arbitrage = {
                    'exchange': exchange,
                    'exch_rate_list': [min_ask['ask_price'], max_bid['bid_price'], min_ask1['ask_price']],
                    'sym_list': arb_list,
                    'spread': fee_adjusted_spread,
                    'initialUSD': depths['initialUSD'],
                    'estimated_profit': spread * depths['initialUSD'],
                    'quantity_list': [min_ask['ask_quantity'], max_bid['bid_quantity'], min_ask1['ask_quantity']],
                    'fee_percentage': fee_percentage
                }
                return arbitrage

            else:
                print("Found Possible Arb but fees are too high")
                return None
        else:
            print("Not a possible arbitrage")
            return None
        return None


    #limit order strategy, if the first coin is already USD or some USD tether
    async def find_tri_arb_opp1_USD(exchange, total_markets, arb_list, fee_percentage = .001):
        # Determine Rates for our 3 currency pairs - order book
        await exchange.load_markets()
        fee_percentage = fee_pcts[exchange.id]
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
        print(arb_list)
        try:
            orderbook1 = await exchange.fetch_order_book(symbol=arb_list[0])
            orderbook2 = await exchange.fetch_order_book(symbol=arb_list[1])
            orderbook3 = await exchange.fetch_order_book(symbol=arb_list[2])
            max_bid = orderbook1['bids'][0]
            min_ask = orderbook2['asks'][0]
            max_bid1 = orderbook3['bids'][0]
        except:
            print ("Has no bids or asks for one of the markets OR not loading orderbook")
            return None
        spread = ((1/max_bid[0]) * min_ask[0] * (1/max_bid1[0])) - 1
        print(spread)
        fee_adjusted_spread = spread - (fee_percentage*3)
        #Sprint((await exchange.fetch_balance())['free'][arb_list[1].split('/')[1]], fee_pcts[exchange.id])
        #depths = await findLowestDepth_with_USD_market(max_bid, min_ask, max_bid1, fee_adjusted_spread, (await exchange.fetch_balance())['free'][arb_list[0].split('/')[1]], fee_pcts[exchange.id])# (await exchange.fetch_balance())['free'][arb_list[1].split('/')[1]])
        depths = await findLowestDepth_with_USD_market(max_bid, min_ask, max_bid1, fee_adjusted_spread, 10000, fee_pcts[exchange.id])
        if spread > 0:
            if (depths['quantity_coin1_final'] - depths['quantity_coin1'])/depths['quantity_coin1'] > 0:
                print("FOUND PROFITABLE ARBITRAGE \n")
                print("--------------------------- \n")
                print("Exchange: {}, Arbitrage: {}".format(exchange.id, arb_list))
                print("REAL PROFIT RATE (BEST CASE SCENARIO): {}".format((depths['quantity_coin1_final'] - depths['quantity_coin1'])/depths['quantity_coin1']))
                print("PROFIT IN TERMS OF STARTING COIN: {}".format((depths['quantity_coin1_final'] - depths['quantity_coin1'])))
                print("QUANTITY OF STARTING COIN (BEST CASE): {} \n".format(max_bid[0] * max_bid[1]))
                print([max_bid[0], min_ask[0], max_bid1[0]])
                arbitrage = {
                    'exchange': exchange,
                    'exch_rate_list': [min_ask['ask_price'], max_bid['bid_price'], min_ask1['ask_price']],
                    'sym_list': arb_list,
                    'spread': fee_adjusted_spread,
                    'initialUSD': depths['initialUSD'],
                    'estimated_profit': spread * depths['initialUSD'],
                    'quantity_list': [min_ask['ask_quantity'], max_bid['bid_quantity'], min_ask1['ask_quantity']],
                    'fee_percentage': fee_percentage
                }
                return arbitrage

            else:
                print("Found Possible Arb but fees are too high")
                return None
        else:
            print("Not a possible arbitrage")
            return None
        return None



    async def find_tri_arb_opp(exchange, total_markets, arb_list, fee_percentage = .001):
        # Determine Rates for our 3 currency pairs - order book
        await exchange.load_markets()
        fee_percentage = fee_pcts[exchange.id]
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
        print(arb_list)
        min_ask = await minAsk(exchange, arb_list[0], total_markets, count)
        max_bid = await maxBid(exchange, arb_list[1], total_markets, count)
        min_ask1 = await minAsk(exchange, arb_list[2], total_markets, count)
        if min_ask['isFound'] and max_bid['isFound'] and min_ask1['isFound']:
            # market_depth_USD = await compute_depth(exchange, arb_list, min_ask, max_bid, min_ask1)
            spread = ((1/min_ask['ask_price']) * max_bid['bid_price'] * (1/min_ask1['ask_price'])) - 1
            print(spread)
            fee_adjusted_spread = spread - (fee_percentage*5)
            depths = await findLowestDepth_with_USD_market(max_bid, min_ask, max_bid1, fee_adjusted_spread, 10000, fee_pcts[exchange.id])
            if spread > 0:
                if fee_adjusted_spread > 0:
                    print("FOUND PROFITABLE ARBITRAGE \n")
                    print("--------------------------- \n")
                    print("Exchange: {}, Arbitrage: {}".format(exchange.id, arb_list))
                    print("REAL PROFIT (BEST CASE SCENARIO): {}".format(fee_adjusted_spread))
                    print("QUANTITY OF STARTING COIN (BEST CASE): {} \n".format(min_ask['ask_price'] * min_ask['ask_quantity']))
                    arbitrage = {
                        'exchange': exchange,
                        'exch_rate_list': [min_ask['ask_price'], max_bid['bid_price'], min_ask1['ask_price']],
                        'sym_list': arb_list,
                        'spread': fee_adjusted_spread,
                        'initialUSD': depths['initialUSD'],
                        'estimated_profit': spread * depths['initialUSD'],
                        'quantity_list': [min_ask['ask_quantity'], max_bid['bid_quantity'], min_ask1['ask_quantity']],
                        'fee_percentage': fee_percentage
                    }
                    return arbitrage

                else:
                    print("Found Possible Arb but fees are too high")
                    return None
            else:
                print("Not a possible arbitrage")
                return None
        return None


    async def findLowestDepth(dollar_exch_bid, bid, ask, bid1, dollar_exch_ask, spread, available_funds_USD, fee_percentage):
        print("SPREAD: {}".format(spread))
        initial_USD = dollar_exch_bid[0] * dollar_exch_bid[1]
        print(initial_USD)
        if initial_USD > available_funds_USD:
            initial_USD = available_funds_USD
        quantity_coin1 = (1-fee_percentage) * initial_USD * (1/dollar_exch_bid[0])
        print(initial_USD, quantity_coin1)

        if (1/bid[0]) * quantity_coin1 > bid[1]:
            quantity_coin1 = bid[0] * bid[1]
            initial_USD = quantity_coin1 * dollar_exch_bid[0]
        quantity_coin2 = (1-fee_percentage) * (1/bid[0]) * quantity_coin1
        print(initial_USD, quantity_coin1, quantity_coin2)

        if quantity_coin2 > ask[1]:
            quantity_coin2 = ask[1]
            quantity_coin1 =  bid[0] * quantity_coin2
            initial_USD = quantity_coin1 * dollar_exch_bid[0]
        quantity_coin3 = (1-fee_percentage) * ask[0] * quantity_coin2
        print(initial_USD, quantity_coin1, quantity_coin2, quantity_coin3)

        if (1/bid1[0]) * quantity_coin3 > bid1[1]:
            quantity_coin3 = bid1[0] * bid1[1]
            quantity_coin2 = quantity_coin3 * (1/ask[0])
            quantity_coin1 = bid[0] * quantity_coin2
            initial_USD = quantity_coin1 * dollar_exch_bid[0]
        quantity_coin1_final = (1-fee_percentage) * (1/bid1[0]) * quantity_coin3
        print(initial_USD, quantity_coin1, quantity_coin2, quantity_coin3, quantity_coin1_final)

        if quantity_coin1_final > dollar_exch_ask[1]:
            quantity_coin1_final = dollar_exch_ask[1]
            quantity_coin3 = bid1[0] * quantity_coin1_final
            quantity_coin2 = quantity_coin3 * (1/ask[0])
            quantity_coin1 = bid[0] * quantity_coin2
            initial_USD = quantity_coin1 * dollar_exch_bid[0]

        final_USD = (1-fee_percentage) * dollar_exch_ask[0] * quantity_coin1_final
        print(initial_USD, quantity_coin1, quantity_coin2, quantity_coin3, quantity_coin1_final, final_USD)
        depth_list = [initial_USD, quantity_coin1, quantity_coin2, quantity_coin3, quantity_coin1_final, final_USD]

        print("\nINITIAL USD INVESTMENT: {}".format(initial_USD))
        print("FINAL USD AMOUNT: {}".format(final_USD))
        print("CALCULATED VOLUME: {}".format(final_USD - initial_USD))
        print("THEORETICAL VOLUME: {}".format(initial_USD * spread))
        depths = {
            'initial_USD': initial_USD,
            'final_USD': final_USD,
            'quantity_coin1': quantity_coin1,
            'quantity_coin2': quantity_coin2,
            'quantity_coin3': quantity_coin3,
            'quantity_list': depth_list,
            'quantity_coin1_final': quantity_coin1_final
        }
        return depths


    async def findLowestDepth_with_USD_market(bid, ask, bid1, spread, available_funds_USD, fee_percentage):
        quantity_coin1 = available_funds_USD
        print(quantity_coin1)

        if (1/bid[0]) * quantity_coin1 > bid[1]:
            quantity_coin1 = bid[0] * bid[1]
        quantity_coin2 = (1-fee_percentage) * (1/bid[0]) * quantity_coin1
        print(quantity_coin1, quantity_coin2)

        if quantity_coin2 > ask[1]:
            quantity_coin2 = ask[1]
            quantity_coin1 =  bid[0] * quantity_coin2
        quantity_coin3 = (1-fee_percentage) * ask[0] * quantity_coin2
        print(quantity_coin1, quantity_coin2, quantity_coin3)

        if (1/bid1[0]) * quantity_coin3 > bid1[1]:
            quantity_coin3 = bid1[0] * bid1[1]
            quantity_coin2 = quantity_coin3 * (1/ask[0])
            quantity_coin1 = bid[0] * quantity_coin2
        quantity_coin1_final = (1-fee_percentage) * (1/bid1[0]) * quantity_coin3
        print(quantity_coin1, quantity_coin2, quantity_coin3, quantity_coin1_final)

        depth_list = [quantity_coin1, quantity_coin2, quantity_coin3, quantity_coin1_final]
        depths = {
            'initial_USD': quantity_coin1,
            'quantity_coin1': quantity_coin1,
            'quantity_coin2': quantity_coin2,
            'quantity_coin3': quantity_coin3,
            'quantity_coin1_final': quantity_coin1_final,
            'quantity_list': depth_list,
            'final_USD': quantity_coin1_final
        }
        return depths

    async def compute_avg_spread(profit_spread_list, profit_dollars_list, quantity_list):
        sum_spread = 0
        sum_dollars = 0
        num = 0

        for i in range(0, len(profit_spread_list)):
            sum_spread += profit_spread_list[i]
            # sum_dollars += profit_dollars_list[i]
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

    def writeToCSV(arbitrageopp):
        i = 0
        if (i == 0):
            thewriter.writerow({'Bot Start Date': current_time.date(), 'Bot Start Time': current_time.time(), 'Exchange': arbitrageopp['exchange'], 'Initial USD': arbitrageopp['initialUSD'], 'First Market': arbitrageopp['sym_list'] [0], 'Second Market': arbitrageopp['sym_list'] [1], 'Third Market': arbitrageopp['sym_list'] [2], 'Spread': arbitrageopp['spread'], 'Estimated Profit': arbitrageopp['estimated_profit']})
        else:
            thewriter.writerow({'Exchange': arbitrageopp['exchange'], 'Initial USD': arbitrageopp['initialUSD'], 'First Market': arbitrageopp['sym_list'] [0], 'Second Market': arbitrageopp['sym_list'] [1], 'Third Market': arbitrageopp['sym_list'] [2], 'Spread': arbitrageopp['spread'], 'Estimated Profit': arbitrageopp['estimated_profit']})
        i+=1

    asyncio.get_event_loop().run_until_complete(run())

    if __name__ == "__main__":
        run()
