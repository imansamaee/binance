import json
import pyperclip

import requests
from binance.enums import SIDE_BUY, SIDE_SELL

from application.home.services.binance.auth import client

class APIData:
    def __init__(self):

        self.is_initialised = False
        self.exchange_info = APIData.get_exchange_info()
        self.symbols_info = self.exchange_info['symbols']
        self.trade_symbols = self.init_trade_symbols()

    def init_trade_symbols(self):
        ts = [ts['symbol'] for ts in self.trading_spot_symbols_info]
        return ts

    @property
    def trading_spot_symbols_info(self):
        return [s for s in self.symbols_info if s['status'] == "TRADING" and "SPOT" in s['permissions']]

    def get_trade_symbol(self, symbol1, symbol2):
        if symbol1 == symbol2:
            print("can not sell itself")
            return None
        for trade_symbol_dict in self.symbols_info:
            trade_symbol = trade_symbol_dict['symbol']
            if symbol1 in trade_symbol and symbol2 in trade_symbol and len(trade_symbol) == (
                    len(symbol1) + len(symbol2)):
                return trade_symbol
        return None

    @staticmethod
    def get_order_side(trade_symbol, crypto_symbol):
        if trade_symbol.startswith(crypto_symbol):
            return SIDE_BUY
        else:
            return SIDE_SELL

    @staticmethod
    def get_exchange_info():
        url = "https://www.binance.com/api/v1/exchangeInfo"
        response = requests.get(url)
        return json.loads(response.text)


if __name__ == "__main__":
    a = APIData()
    pyperclip.copy(json.dumps(client.get_account()))
