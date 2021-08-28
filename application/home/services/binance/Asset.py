import json
import operator

import requests

from application.home.services.binance import logger
from application.home.services.binance.auth import client
from application.home.services.binance.crypto import Crypto


class Asset:
    # test
    def __init__(self):
        """
        this class contains all the assets in binance account.
        """
        logger.info("Asset initiated...")
        self.crypto_list = []
        self.available_crypto_list = []
        self.init_fiat_balance = None
        self.current_fiat_balance = None
        self.init_overall_balance = 0
        self.last_fiat_balance = 0
        self.overall_balance = 0
        self.is_initialised = False
        self.api_balances = client.get_account()['balances']
        self.trade_symbol_list = None
        self.init_crypto_list()
        self.prices_jason = self.get_prices_jason()
        self.last_sell = None
        self.last_overall_balance = None

    def init_crypto_list(self):
        self.update_prices()
        self.init_overall_balance = self.get_overall_balance()
        self.is_initialised = True

    def get_available_crypto_list(self):
        self.available_crypto_list = sorted([i for i in self.crypto_list if i.balance > 0],
                                            key=operator.attrgetter("fiat_balance"), reverse=True)

    def is_crypto_available(self, symbol):
        return len([c for c in self.crypto_list if c.symbol == symbol]) > 0

    # request here only
    def update_prices(self):
        _json = Asset.get_prices_jason()
        self.trade_symbol_list = [t['symbol'] for t in _json]
        if self.init_overall_balance == 0:
            self.init_overall_balance = self.get_init_overall_balance()

        if not self.is_initialised:
            logger.info("Initiating Cryptos...")
        for balance in self.api_balances:
            symbol = balance['asset']
            if symbol == "USDT":
                continue
            if symbol + "USDT" in self.trade_symbol_list:
                price = Asset.get_price(_json, symbol, "USDT")
            elif symbol + "BTC" in self.trade_symbol_list:
                price = Asset.get_price(_json, symbol, "BTC") * Asset.get_price(_json, "BTC", "USDT")
            elif symbol + "BNB" in self.trade_symbol_list:
                price = Asset.get_price(_json, symbol, "BNB") * Asset.get_price(_json, "BNB", "USDT")
            else:
                continue
            if not self.is_initialised:
                crypto = Crypto(balance['asset'])
                crypto.current_price = price
                crypto.start_price = price
                crypto.balance = float(balance['free'])
                self.crypto_list.append(crypto)
            else:
                crypto = self.get_crypto_by_symbol(symbol)
                crypto.balance = float(balance['free'])
                # if symbol == "BTC":
                #     print(f"price = {price}")
                crypto.current_price = price
        self.get_available_crypto_list()
        self.overall_balance = self.get_overall_balance()

    @staticmethod
    def get_price(_json, symbol, end_symbol):
        try:
            return float(next(filter(lambda c: c['symbol'] == symbol + end_symbol, _json))['price'])
        except StopIteration:
            logger.error(f"Crypto {symbol} not in current Assets.")
            return None

    def get_symbols_by_trade_symbol(self, trade_symbol):
        first_symbol = ""
        second_symbol = ""
        for crypto in self.crypto_list:
            if crypto.symbol in trade_symbol:
                first_symbol = crypto.symbol
                second_symbol = trade_symbol.replace(first_symbol, "")
                second_crypto = self.get_crypto_by_symbol(second_symbol)
                if not second_crypto:
                    continue
                if second_symbol in trade_symbol and len(first_symbol) + len(second_symbol) == len(trade_symbol):
                    break
        # if first_symbol == "" or second_symbol =="":
        #     print(f"trade is wrong: {trade_symbol}")
        return [first_symbol, second_symbol]

    def get_overall_balance(self):
        fiat = 0
        for crypto in self.crypto_list:
            fiat += crypto.balance * crypto.current_price
        return fiat

    def get_crypto_by_symbol(self, symbol):
        try:
            return next(filter(lambda c: c.symbol == symbol, self.crypto_list))
        except StopIteration:
            # logger.error(f"Crypto {symbol} not in current Assets.")
            return None

    def get_init_overall_balance(self):
        fiat = 0
        for crypto in self.crypto_list:
            fiat += crypto.balance * crypto.start_price
        return fiat

    def reset_cryptos(self):
        for crypto in self.crypto_list:
            crypto.reset()

    @staticmethod
    def get_prices_jason():
        # array of trade symbol and prices only
        url = "https://api.binance.com/api/v3/ticker/price"
        response = requests.get(url)
        return json.loads(response.text)
