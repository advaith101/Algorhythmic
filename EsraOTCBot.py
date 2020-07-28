import time
from typing import Optional, Any
from requests import Request, Session, Response
from typing import Dict
import hmac
import ccxtpro
import ccxt
import datetime
import random
from pprint import pprint
import asyncio


class FtxOtcClient:
    _ENDPOINT = 'https://otc.ftx.com/api/'

    def __init__(self) -> None:
        self._session = Session()
        self._api_key = '45S6wYBHTThYSEXawgMmZp7pfK16dXLGsU497Td7' # TODO: Place your API key here
        self._api_secret = 'oZzTfbjydjbyiTbnQa-wB9sSUlhjR3FFyWSbNJz6' # TODO: Place your API secret here

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('GET', path, params=params)

    def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('POST', path, json=params)

    def _delete(self, path: str) -> Any:
        return self._request('DELETE', path)

    def request_otc_quote(self, base_currency: str, quote_currency: str, side: str,
                          base_currency_size: Optional[float] = None,
                          quote_currency_size: Optional[float] = None,
                          wait_for_price: bool = True) -> Any:
        assert (quote_currency_size is None) ^ (base_currency_size is None)
        return self._post('otc/quotes', {
            'baseCurrency': base_currency,
            'quoteCurrency': quote_currency,
            'baseCurrencySize': base_currency_size,
            'quoteCurrencySize': quote_currency_size,
            'waitForPrice': wait_for_price,
            'side': side,
        })

    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._ENDPOINT + path, **kwargs)
        self._sign_request(request, path)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _sign_request(self, request: Request, path: str) -> None:
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}/{path}'.encode()
        if prepared.body:
            signature_payload += prepared.body
        signature = hmac.new(self._api_secret.encode(), signature_payload, 'sha256').hexdigest()
        request.headers['FTX-APIKEY'] = self._api_key
        request.headers['FTX-TIMESTAMP'] = str(ts)
        request.headers['FTX-SIGNATURE'] = signature

    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                raise Exception(data['error'])
            return data['result']

    def get_balances(self):
        return self._get('balances')



async def run():
    client = FtxOtcClient()
    # res = client._get('otc/pairs')
    # print(res)
    await config_arbitrages(client)

async def config_arbitrages(client):
    print("\n\n ----------------------------------- \n\n")
    print("\n\nEsra FTX OTC Triangular Arbitrage Bot Running....\n\n")
    print("Copyright 2020 Esra Systems All Rights Reserved visit www.esrainvestments.com for more info\n\n")
    print("\n\n ----------------------------------- \n\n")
    time.sleep(2)
    list_of_arb_lists = []
    symbols = client._get('otc/pairs')
    # quotes = client._get('otc/quotes')
    print(symbols)
    # for symb in symbols:
    #     arb_list = [symb['']]
    #     j = 0
    #     while 1:
    #         if j >= 1:
    #             if len(arb_list) > 1:
    #                 final = arb_list[0].split('/')[1] + '/' + str(arb_list[1].split('/')[1])
    #                 # print(final)
    #                 if final in exchange1.symbols:
    #                     arb_list.append(final)
    #                 # elif arb_list[1].split('/')[1] + '/' + str(arb_list[0].split('/')[1]) in exchange1.symbols:
    #                 #     arb_list.append(arb_list[1].split('/')[1] + '/' + str(arb_list[0].split('/')[1]))
    #             break
    #         for sym in symbols:
    #             if sym in arb_list:
    #                 continue
    #             if arb_list[0].split('/')[0] == sym.split('/')[0]:
    #                 if arb_list[0] == sym:
    #                     continue
    #                 else:
    #                     arb_list.append(sym)
    #                     j += 1
    #                     break
    #         j += 1
    #     if len(arb_list) > 2:
    #         # print(arb_list[2])
    #         if arb_list[2] in exchange1.symbols:
    #             # print(arb_list)
    #             list_of_arb_lists.append(arb_list)

    # print("\nList of Arbitrage Symbols:", list_of_arb_lists)





asyncio.get_event_loop().run_until_complete(run())

if __name__ == "__main__":
    run()
