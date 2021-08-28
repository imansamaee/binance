import operator

from binance.enums import ORDER_TYPE_LIMIT, TIME_IN_FORCE_GTC
from binance.exceptions import BinanceAPIException

from application.home.services.binance import API_DATA, APIData, logger
from application.home.services.binance.Asset import Asset
from application.home.services.binance.auth import client
from application.home.services.binance.exchange import Exchange
from application.home.services.binance.nominee import Nominee


class Trade:
    def __init__(self):
        logger.info("Trade initiated...")
        self.asset = Asset()
        self.nominee = Nominee()
        self.sell_price = 0
        self.skip_trade = 0
        self.max_skip_trade = 15
        self.max_rounds = 10 * 30
        self.counter_speed = 1
        self.init_counter = 0  # self.max_rounds - self.max_skip_trade - 20
        self.counter = self.init_counter
        self.acceptable_profit = 0.01
        self.commission = 0.001
        self.is_initiated = False
        self.last_sell_fiat = 0
        self.current_trade = None
        self.available_cryptos_to_trade = []
        self._available_crypto_symbols_to_trade = None
        self.force_buy_init = False
        self.ignore_on_this_trade_symbols = []
        self.current_normalized_profit = 50
        self.forced_buy_applied = False
        self.skipping_trades = False
        self._limited_sell = False
        self.in_the_red = False
        self._init_buy_nominee = []
        self.middle_man = False

    def update_assets(self):
        if self.check_skipping():
            return
        if not self.asset.is_initialised:
            self.asset.init_crypto_list()
        self.asset.update_prices()
        self.update_nominees()
        self.evaluate_limit()
        self.evaluate_stop()

        self.counter += 1 * self.counter_speed

    def check_skipping(self):
        self.skipping_trades = self.skip_trade < self.max_skip_trade
        self.skip_trade += 1
        return self.skipping_trades

    def evaluate_stop(self):
        # case one: when BTC and ETH and ... are not available in start for first run
        if self.limited_sell and self.counter > 5 and self.asset.last_sell is None:
            self.nominee.best_buy = self.available_cryptos_to_trade[0]
            print(
                f"Force limited buy approved for first time running. Sell is forced to {self.nominee.best_buy.symbol}")
            self.commit_trade()

            return
        # case two: when we don't want to wait for nominees. We want to sell BTC,... ASAP
        if not self.limited_sell and self.nominee.best_buy is not None:
            self.nominee.best_buy = self.available_cryptos_to_trade[0]
            print(f"Force limited buy approved. Sell is forced to {self.nominee.best_buy.symbol}")
            self.commit_trade()
            self.middle_man = True
            return

        # case three:
        if self.counter > self.max_rounds:
            if self.nominee.best_buy is not None:
                print("Force buy approved.")
                self.commit_trade()
                self.middle_man = False
                return

            else:
                self.counter = 0
                self.forced_buy_applied = True
        if self.nominee.best_buy and self.forced_buy_applied:
            self.commit_trade()
            self.middle_man = False
        return

    @property
    def limited_sell(self):
        self._limited_sell = 0 < len(self.available_cryptos_to_trade) < 10
        return self._limited_sell

    @property
    def total_profit(self):
        return self.asset.init_fiat_balance - self.asset.current_fiat_balance

    @property
    def current_profit(self):
        return self.asset.current_fiat_balance - self.asset.last_fiat_balance

    @property
    def available_crypto_symbols_to_trade(self):
        if not self.nominee.sell:
            return
        _available_crypto_symbols_to_trade = []

        if not self.nominee.sell:
            return _available_crypto_symbols_to_trade
        # print(self.asset.trade_symbol_list)
        for trade_symbol in self.asset.trade_symbol_list:
            if self.nominee.sell.symbol in trade_symbol:
                status = Exchange.get_symbol_info(trade_symbol)['status']
                if status != "TRADING":
                    continue
                other_symbol = trade_symbol.replace(self.nominee.sell.symbol, "")
                if other_symbol and self.asset.is_crypto_available(other_symbol):
                    _available_crypto_symbols_to_trade.append(other_symbol)
        self._available_crypto_symbols_to_trade = list(dict.fromkeys(_available_crypto_symbols_to_trade))
        # print(self._available_crypto_symbols_to_trade)
        self.available_cryptos_to_trade = sorted(
            [self.asset.get_crypto_by_symbol(i) for i in self._available_crypto_symbols_to_trade],
            key=operator.attrgetter("bounce"),
            reverse=True)
        self._available_crypto_symbols_to_trade = [i.symbol for i in self.available_cryptos_to_trade]
        if not self.limited_sell:
            self.counter_speed = 5
        else:
            self.counter_speed = 1
        return self._available_crypto_symbols_to_trade

    @property
    def init_buy_nominee(self):
        if self.limited_sell:
            self._init_buy_nominee = self.available_cryptos_to_trade
        else:
            self._init_buy_nominee = []
            for crypto in self.available_cryptos_to_trade:
                if crypto.bounce < 1:
                    continue
                self._init_buy_nominee.append(crypto)
        return self._init_buy_nominee

    def commit_trade(self):
        try:
            sell = self.nominee.sell.symbol
            buy = self.nominee.best_buy.symbol
            symbol = API_DATA.get_trade_symbol(sell, buy)
            exchange = Exchange(symbol)
            side = APIData.get_order_side(symbol, buy)
            quantity_and_price = exchange.get_quantity_and_price(self.nominee.sell, self.nominee.best_buy, symbol, side)
            print("Starting Trade...")
            self.skip_trade = 0

            trade = client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC,
                price=quantity_and_price['price'],
                quantity=quantity_and_price['qty']
            )
            print("done!")
            if trade:
                self.sell_price = self.nominee.best_buy.current_price
                self.finalize_sell(trade)
                self.counter = 0
            else:
                logger.error("Unknown Error. transfer unsuccessful!")
        except BinanceAPIException as e:
            print(f"Trade Failed! {e.message}")
            logger.error(f"Binance Error: {e.message}")

    def update_nominees(self):
        if not self.get_sell_nominee():
            return
        if len(self.available_crypto_symbols_to_trade) == 0:
            return
        self.nominee.buy_list = []
        for crypto in self.init_buy_nominee:
            if not crypto:
                continue
            if not Exchange.check_exchange(self.nominee.sell.symbol, crypto.symbol):
                return

            # if crypto.bounce.ready_to_buy and crypto.symbol in self.available_crypto_symbols_to_trade:
            if crypto not in self.nominee.buy_list:
                if crypto.position < 30 and crypto.bounce > 0:
                    self.nominee.buy_list.append(crypto)
                    self.nominee.buy_list = sorted(self.nominee.buy_list,
                                                   key=operator.attrgetter("position"),
                                                   reverse=False)
            self.nominee.best_buy = None
            if len(self.nominee.buy_list) > 0:
                if self.nominee.buy_list[0] != self.asset.last_sell:
                    self.nominee.best_buy = self.nominee.buy_list[0]
                elif len(self.nominee.buy_list) > 1:
                    self.nominee.best_buy = self.nominee.buy_list[1]

    def get_sell_nominee(self):
        if len(self.asset.available_crypto_list) > 0:
            self.nominee.sell = self.asset.available_crypto_list[0]
            return self.nominee.sell

    def finalize_sell(self, trade):
        if not self.middle_man:
            self.asset.reset_cryptos()
        self.forced_buy_applied = False
        self.current_trade = trade
        print(f"Trade result is {trade}")
        # after selling the best_buy
        self.set_last_fiat_balance(trade)
        self.nominee.last_sell = self.nominee.sell
        self.nominee.last_buy = self.nominee.best_buy
        if self.nominee.best_buy in self.nominee.buy_list:
            self.nominee.buy_list.remove(self.nominee.best_buy)
        self.nominee.sell = self.nominee.best_buy
        self.nominee.best_buy = None
        self.asset.api_balances = client.get_account()['balances']
        self.counter = 1
        self.force_buy_init = True
        if not self.force_buy_init:
            self.counter = self.max_rounds - self.max_skip_trade
        self.force_buy_init = False
        print(f"{self.last_sell_fiat} USD Trade committed!")
        self.ignore_on_this_trade_symbols = []

    def evaluate_limit(self):
        if self.sell_price == 0:
            return False
        if self.nominee.sell:
            if self.nominee.sell.position > 70 and not self.middle_man:
                print("Profit approved!")
                self.commit_trade()
                return True
        sell_price = self.sell_price
        current_price = self.nominee.sell.current_price
        commission = self.commission
        acceptable_profit = self.acceptable_profit
        acceptable_price_profit = sell_price * acceptable_profit
        profit = current_price - (sell_price * (1 - commission))

        current_normalized_profit = 50 + round(profit / acceptable_price_profit * 5000) / 100
        self.current_normalized_profit = current_normalized_profit
        if profit < 0:
            self.in_the_red = True
        else:
            self.in_the_red = False

        # if self.current_normalized_profit >= 100:
        #     if self.nominee.best_buy is None:
        #         self.nominee.best_buy = self.available_cryptos_to_trade[0]
        #     print("Profit approved!")
        #     return True
        return False

    def set_last_fiat_balance(self, trade):
        if trade['fills']:
            base_crypto = self.asset.get_crypto_by_symbol(trade['fills'][0]['commissionAsset'])
            qty = float(trade['fills'][0]['qty'])

            self.asset.last_overall_balance = self.asset.overall_balance
            self.last_sell_fiat = base_crypto.current_price * qty
