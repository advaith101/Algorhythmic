async def execute_all_tri_arb_orders(list_of_lists_of_arb_lists):
    #Determines profitability and executes profitable orders.
    profit_spread_list = []
    profit_dollars_list = []
    quantity_list1 =[]
    for list_of_arb_lists in list_of_lists_of_arb_lists:
        exchange = list_of_arb_lists[0]
        markets = list_of_arb_lists[2]
        for arb_list in list_of_arb_lists[1]:
            arbitrageopp = await find_tri_arb_opp1(exchange, markets, arb_list)
            try:
                if(arbitrageopp['profit'] > 0.0):
                    symbol1 = markets[0].split('/')[0]
                    USDmarket = symbol1 + '/USD'
                    USD_order_book = fetch_order_book(symbol = USDmarket)
                    profit_spread_list.append(arbitrageopp['profit'])
                    quantity_list1.append([arbitrageopp['sym_list'][0], arbitrageopp['quantity_list'][0]])
                    profit_dollars_list.append(arbitrageopp['profit_in_dollars'])
                    quantity_list = arbitrageopp['quantity_list']
                    depths = findLowestDepth(USD_order_book['bids'][0], bid, ask, bid1, USD_order_book['asks'][0], spread, available_funds_USD, fee_percentage)

                    # await pre_tri_arb_USD_transfer(arbitrageopp['exchange'], arbitrageopp['sym_list'], arbitrageopp['fee_percentage'], quantity_list[0])
                    # quantity_3 = tri_arb_orders(arbitrageopp['exchange'], arbitrageopp['exch_rate_list'], arbitrageopp['sym_list'], arbitrageopp['quantity_list'], arbitrageopp['fee_percentage'])
                    # await post_tri_arb_USD_transfer(arbitrageopp['exchange'],  arbitrageopp['sym_list'], arbitrageopp['fee_percentage'], quantity_list[2])
                    print("\nOrdering should be complete by this point\n")
            except:
                print("\n\nNo Arbitrage Possibility\n\n")
    return profit_spread_list, profit_dollars_list, quantity_list1

async def findLowestDepth(dollar_exch_bid, bid, ask, bid1, dollar_exch_ask, spread, available_funds_USD, fee_percentage):
    print("SPREAD: {}".format(spread))
    initial_USD = dollar_exch_bid[0] * dollar_exch_bid[1]
    if initial_USD > available_funds_USD:
        initial_USD = available_funds_USD
    quantity_coin1 = (1-fee_percentage) * initial_USD * (1/dollar_exch_bid[0])
    if (1/bid[0]) * quantity_coin1 > bid[1]:
        quantity_coin1 = bid[0] * bid[1]
        initial_USD = quantity_coin1 * dollar_exch_bid[0]
    quantity_coin2 = (1-fee_percentage) * bid[1]
    if quantity_coin2 > ask[1]:
        quantity_coin2 = ask[1]
        quantity_coin1 = bid[0] * quantity_coin2
        initial_USD = quantity_coin1 * dollar_exch_bid[0]
    quantity_coin3 = (1-fee_percentage) * ask[0] * quantity_coin2
    if (1/bid1[0]) * quantity_coin3 > bid1[1]:
        quantity_coin3 = bid1[0] * bid1[1]
        quantity_coin2 = quantity_coin3 * (1/ask[0])
        quantity_coin1 = bid[0] * quantity_coin2
        initial_USD = quantity_coin1 * dollar_exch_bid[0]
    quantity_coin1_final = (1-fee_percentage) * bid1[1]
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
    depths = {
        'initial_USD': initial_USD,
        'final_USD': final_USD,
        'quantity_coin1': quantity_coin1,
        'quantity_coin2': quantity_coin2,
        'quantity_coin3': quantity_coin3,
        'quantity_coin1_final': quantity_coin1_final
    }
    return depths


async def findLowestDepth_with_USD_market(bid, ask, bid1, spread, available_funds_USD):
    quantity_coin1 = available_funds_USD
    if (1/bid[0]) * quantity_coin1 > bid[1]:
        quantity_coin1 = bid[0] * bid[1]
        initial_USD = quantity_coin1 * dollar_exch_bid[0]
    quantity_coin2 = (1-fee_percentage) * bid[1]
    if quantity_coin2 > ask[1]:
        quantity_coin2 = ask[1]
        quantity_coin1 = bid[0] * quantity_coin2
        initial_USD = quantity_coin1 * dollar_exch_bid[0]
    quantity_coin3 = (1-fee_percentage) * ask[0] * quantity_coin2
    if (1/bid1[0]) * quantity_coin3 > bid1[1]:
        quantity_coin3 = bid1[0] * bid1[1]
        quantity_coin2 = quantity_coin3 * (1/ask[0])
        quantity_coin1 = bid[0] * quantity_coin2
        initial_USD = quantity_coin1 * dollar_exch_bid[0]
    quantity_coin1_final = (1-fee_percentage) * bid1[1]
    depths = {
        'initial_USD': quantity_coin1,
        'quantity_coin2': quantity_coin1,
        'quantity_coin3': quantity_coin1,
        'final_USD': quantity_coin1_final
    }
    return depths

async def checkforOpenOrders(exchange, market):
    i = 0
    isOpenOrder = True
    while isOpenOrder:
        if exchange.fetch_order_book(symbol = 'market') == '':
            isOpenOrder = False
        i++
    print('Order Complete')
