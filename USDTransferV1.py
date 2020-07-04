import ccxt
import time
import random
from pprint import pprint

#NOTES: Looking through the Bid Order Book, Ask Order Book, how can we find the best deal for a bid price or ask price? Or should the bid order or ask order be a market order placement?
def pre_tri_arb_USD_transfer(exchange, sym_list, fee_percentage, quantity_1): #make exchange, exch_rate_list, sym_list, fee_percentage global vars
    market1 = sym_list[0]
    USDmarket = market1[0:3] + "/USDC"
    print("Transferring capital in USDC to " + market1)
    depth = exchange.fetch_order_book(symbol = USDmarket)
    USD_sell_exch_rate = round(maxBid(exchange, market1)) #is this the highest volume in the bid order book... should it be a limit or market order?
    print(USD_sell_exch_rate)
    non_fee_adjusted_quantity = quantity_1/USD_sell_exch_rate
    print(non_fee_adjusted_quantity)
    totalprice = non_fee_adjusted_quantity * USD_sell_exch_rate
    fee_adjusted_quantity = (totalprice + (totalprice * (fee_percentage / 100))) / USD_sell_exch_rate
    print(fee_adjusted_quantity)
    pre_USD_transfer_order = client.create_order(symbol=USDmarket,
                                      side=SIDE_SELL,
                                      type=ORDER_TYPE_LIMIT,
                                      quantity=fee_adjusted_quantity, #compensating for fees so we receive the correct quantity_1
                                      price=USD_sell_exch_rate,
                                      timeInForce=TIME_IN_FORCE_GTC)
    print("Pre Tri Arb Coin Transfer Complete")

def post_tri_arb_USD_transfer(exchange,  sym_list, fee_percentage, quantity_3):
    market1 = sym_list[0]
    USDmarket = market1[0:3] + "/USDC"
    print("Transfering capital in " + USDmarket + " to USDC")
    depth = exchange.fetch_order_book(symbol = USDmarket)
    USD_buy_exch_rate = round(minAsk(exchange, market1))
    post_USD_transfer_order = client.create_order(symbol=USDmarket,
                                  side=SIDE_BUY,
                                  type=ORDER_TYPE_LIMIT,
                                  quantity=quantity_3,
                                  price=(1/USD_buy_exch_rate),
                                  timeInForce=TIME_IN_FORCE_GTC)
    print("Post Tri Arb Coin Transfer Complete")

#Testing
sym_list = ["BNB/ETH", "ETH/USDT", "BNB/USDT"]
exchange = ccxt.binance()
fee_percentage = .1
quantity_1 = 5
pre_tri_arb_USD_transfer(exchange, sym_list, fee_percentage, quantity_1)
quantity_3 = 6
post_tri_arb_USD_transfer(exchange, sym_list, fee_percentage, quantity_3)
