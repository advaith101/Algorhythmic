import ccxtpro
import datetime
import time
import random
from pprint import pprint
import asyncio

transfer_symbol = 'USDC'
amount_digits_rounded = 5


async def run():
    # exchange = ccxtpro.binance()
    # await exchange.load_markets()
    # test = exchange.symbols
    # print(test)
    
    list_of_lists_of_arb_lists = await config_arbitrages()
    while 1:
        profit_spread_list = await execute_all_tri_arb_orders(list_of_lists_of_arb_lists)
        await compute_avg_spread(profit_spread_list)
        print("CYCLE FINISHED, STARTING NEXT CYCLE...")
        await asyncio.sleep(3)

async def config_arbitrages():
    print("\n\n ----------------------------------- \n\n")
    print("\n\nEsra Unified Crypto Arbitrage Finder Running....\n\n")
    print("Copyright 2020 Esra Systems All Rights Reserved visit www.esrainvestments.com for more info\n\n")
    print("\n\n ----------------------------------- \n\n")
    time.sleep(2)
    markets = {}
    list_of_lists_of_arb_lists = []
    for exch in ccxtpro.exchanges:  # initialize Exchange
        exchange1 = getattr(ccxtpro, exch)()
        try:
            val = await exchange1.load_markets()
            markets = val.keys()
        except:
            print('\nExchange is not loading markets.. Moving on\n')
        print("Exchange Name: {}".format(exchange1.id))
        symbols = exchange1.symbols
        # print(symbols)
        if symbols is None:
            print("Skipping Exchange ", exch)
            print("\n-----------------\nNext Exchange\n-----------------")
        elif len(symbols) < 30:
            print("\n-----------------\nNeed more Pairs (Next Exchange)\n-----------------")
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
                    if arb_list[0] in markets and arb_list[1] in markets and arb_list[2] in markets:
                        print(arb_list)
                        list_of_arb_lists.append(arb_list)
                        list_of_arb_listswmarkets.append([arb_list, markets])
            print("\nList of Arbitrage Symbols:", list_of_arb_lists)
            list_of_lists_of_arb_lists.append([exchange1, list_of_arb_lists])
    return list_of_lists_of_arb_lists



async def execute_all_tri_arb_orders(list_of_lists_of_arb_lists):
    #Determines profitability and executes profitable orders.
    profit_spread_list = []
    for list_of_arb_lists in list_of_lists_of_arb_lists:
        exchange = list_of_arb_lists[0]
        var = await exchange.load_markets()
        markets = var.keys()
        for arb_list in list_of_arb_lists[1]:
            # print("{} \n".format(exchange1))
            # print("{} \n".format(markets))
            # print("{} \n".format(arb_list))
            # arbitrageopp = asyncio.gather(await find_tri_arb_opp(exchange1, list(markets), arb_list))
            arbitrageopp = await find_tri_arb_opp(exchange, markets, arb_list)
            if(arbitrageopp['profit'] > 0.0):
                profit_spread_list.append(arbitrageopp['profit'])
                quantity_list = arbitrageopp['quantity_list']
                # await pre_tri_arb_USD_transfer(arbitrageopp['exchange'], arbitrageopp['sym_list'], arbitrageopp['fee_percentage'], quantity_list[0])
                # quantity_3 = tri_arb_orders(arbitrageopp['exchange'], arbitrageopp['exch_rate_list'], arbitrageopp['sym_list'], arbitrageopp['quantity_list'], arbitrageopp['fee_percentage'])
                # await post_tri_arb_USD_transfer(arbitrageopp['exchange'],  arbitrageopp['sym_list'], arbitrageopp['fee_percentage'], quantity_3)
                print("\nOrdering should be complete by this point\n")
    return profit_spread_list


async def find_tri_arb_opp(exchange, total_markets, arb_list, fee_percentage = .001):
    # Determine Rates for our 3 currency pairs - order book
    await exchange.load_markets()
    opp_exch_rate_list = []
    opp_quantity_list = []
    opp_max_bid_price_quantity = []
    list_exch_rate_list = []
    exch_rate_list = []
    
    i = 0
    print("\nChecking for profit: ")
    for sym in arb_list:
        # print(sym)
        if sym in exchange.symbols:
            if i % 2 == 0:
                opp_max_bid_price_quantity = await maxBid(exchange, sym, total_markets)
                # assumed trade volume of $100
                if opp_max_bid_price_quantity['isFound']:
                    exch_rate_list.append(opp_max_bid_price_quantity['bid_price'])
                    print("Max Bid Price: {}".format(opp_max_bid_price_quantity['bid_price']))
                    opp_quantity_list.append(opp_max_bid_price_quantity['bid_quantity'])
                    # opp_max_bid_price_quantity['bid_quantity']
                else:
                    print("\nCould not find a bid_price or bid_quantity\n")
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
                    exch_rate_list.append(0)
            i += 1
        else:
            exch_rate_list.append(0)
        # exch_rate_list.append(((rateB[-1]-rateA[-1])/rateA[-1])*100)  #Expected Profit
        # print("Exchange Rate List: {}".format(exch_rate_list))
        # Compare to determine if Arbitrage opp exists
    try:
        if exch_rate_list[0] < exch_rate_list[1]/exch_rate_list[2]:
            # calculate real rate!!!
            exchangeratespread = (exch_rate_list[1]/exch_rate_list[2]) - exch_rate_list[0]
            opp_exch_rate_list = exch_rate_list
            print("Arbitrage Possibility")
        else:
            print("No Arbitrage Possibility")
    except:
        print("No Arbitrage Possibility")
        # Format data (list) into List format (list of lists)
        # list_exch_rate_list.append(exch_rate_list)

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
        profit = (rateB-rateA) - (fee_percentage * 5)
        # if profit > 0:
        #     print("Original Exchange Rate: {} \nArbitrage Exchange Rate: {} \nArbitrage Exchange Rate including Fees: {} \nReal Profit: {}".format(rateA, rateB, rateB_fee, profit))
    except:
        print("One of the rates is 0. Which means minAsk or maxBid returned 0 for ask_price or bid_price respectively. Which prolly means no asks or bids > 100$.")
    if profit > 0 and rateA != 0:
        print("FOUND PROFITABLE ARBITRAGE \n")
        print("--------------------------- \n")
        total_fee_pct = fee_percentage * 5
        print("Exchange: {}, Arbitrage: {}, Original Exchange Rate: {}, Arbitrage Exchange Rate: {}, Fee Rate: {}".format(exchange.id, arb_list, rateA, rateB, total_fee_pct))
        print("REAL PROFIT: {} \n".format(profit))
        #profit_spread_list.append(profit)
        #profit_volume_list.append()

    #exchange.close()
    arbitrage = {
        'exchange': exchange,
        'sym_list': arb_list,
        'exch_rate_list': opp_exch_rate_list, #maxBid, minAsk, maxBid
        'profit': profit,
        'quantity_list': opp_quantity_list,
        'fee_percentage': fee_percentage
    }
    return arbitrage

async def maxBid(exchange, market, total_markets, min_USD_for_trade=100):
    await exchange.load_markets()
    price_quantity = {}
    finalmarket = ''
    USDmarket = market[0:3] + "/USD"
    USDCmarket = market[0:3] + "/USDC"
    USDTmarket = market[0:3] + "/USDT"
    try:
        if USDmarket in total_markets:
            finalmarket = USDmarket
            USDdepth = await exchange.fetch_order_book(symbol=finalmarket)
            min_quantity = round(float(min_USD_for_trade/(USDdepth['bids'][0][0])), amount_digits_rounded)
        elif USDCmarket in total_markets:
            finalmarket = USDCmarket
            USDdepth = await exchange.fetch_order_book(symbol=finalmarket)
            min_quantity = round(float(min_USD_for_trade/(USDdepth['bids'][0][0])), amount_digits_rounded)
        elif USDTmarket in total_markets:
            finalmarket = USDTmarket
            USDdepth = await exchange.fetch_order_book(symbol=finalmarket)
            min_quantity = round(float(min_USD_for_trade/(USDdepth['bids'][0][0])), amount_digits_rounded)
        else:
            price_quantity = {
                'bid_price': 0,
                'bid_quantity': 0,
                'isFound': False
            }
            print("Cannot find compatible USD/USDC/USDT market")
            return price_quantity
    except:
        print('has no bids for USDC/USDT/USD')
    try:
        depth = await exchange.fetch_order_book(symbol=market)
        for bid in depth['bids']:
            if bid[1] > min_quantity:
                rounded_bid_price = round(float(bid[0]),amount_digits_rounded)
                rounded_bid_quantity = round(float(bid[1]),amount_digits_rounded)
                price_quantity = {
                    'bid_price': rounded_bid_price,
                    'bid_quantity': rounded_bid_quantity,
                    'isFound': True
                }
                return price_quantity
        price_quantity = {
            'bid_price': rounded_bid_price,
            'bid_quantity': rounded_bid_quantity,
            'isFound': False
        }
        print("Could not find a bid above minimum quantity")
        return price_quantity
    except:
        price_quantity = {
            'bid_price': 0,
            'bid_quantity': 0,
            'isFound': False
        }
        print("Error with Max Bid")
        return price_quantity

async def minAsk(exchange, market, total_markets, min_USD_for_trade = 100):
    await exchange.load_markets()
    price_quantity = {}
    price_quantity = {}
    finalmarket = ''
    USDmarket = market[0:3] + "/USD"
    USDCmarket = market[0:3] + "/USDC"
    USDTmarket = market[0:3] + "/USDT"
    try: 
        if USDmarket in total_markets:
            finalmarket = USDmarket
            USDdepth = await exchange.fetch_order_book(symbol=finalmarket)
            min_quantity = round(float(min_USD_for_trade/(USDdepth['asks'][0][0])), amount_digits_rounded)
        elif USDCmarket in total_markets:
            finalmarket = USDCmarket
            USDdepth = await exchange.fetch_order_book(symbol=finalmarket)
            min_quantity = round(float(min_USD_for_trade/(USDdepth['asks'][0][0])), amount_digits_rounded)
        elif USDTmarket in total_markets:
            finalmarket = USDTmarket
            USDdepth = await exchange.fetch_order_book(symbol=finalmarket)
            min_quantity = round(float(min_USD_for_trade/(USDdepth['asks'][0][0])), amount_digits_rounded)
        else:
            price_quantity = {
                'ask_price': 0,
                'ask_quantity': 0,
                'isFound': False
            }
            print("Cannot find compatible USD/USDC/USDT market")
            return price_quantity
    except:
        print('has no asks for USDC/USDT/USD')
    try:
        depth = await exchange.fetch_order_book(symbol = market)
        for ask in depth['asks']:
            if ask[1] > min_quantity:
                rounded_ask_price = round(float(ask[0]),amount_digits_rounded)
                rounded_ask_quantity = round(float(ask[1]),amount_digits_rounded)
                price_quantity = {
                    'ask_price': rounded_ask_price,
                    'ask_quantity': rounded_ask_quantity,
                    'isFound': True
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


async def compute_avg_spread(profit_spread_list):
    sum_spread = 0
    num = 0
    for spread in profit_spread_list:
        sum_spread += spread
        num += 1
    print("AVERAGE SPREAD: {}".format(sum_spread/num))
    print("AVERAGE PROFIT VOLUME (assuming all trades have the minimum volume of $100): {}".format((sum_spread/num)*100))
    return sum_spread/num



asyncio.get_event_loop().run_until_complete(run())

if __name__ == "__main__":
    run()
