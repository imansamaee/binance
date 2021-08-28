class Crypto:

    def __init__(self, crypto_symbol):
        self.symbol = crypto_symbol
        self.bounce = 0
        self.current_bounce = 0
        self.reset_rounds = 30 * 30
        self._current_price = 0
        self.start_price = 0
        self.alpha = 1
        self.beta = 0
        self.round = 0
        self.delta = 1
        self.gamma = 0
        self.total_price = 0
        self.average_price = 0
        self.high_delta = -1000
        self.low_delta = 1000
        self.overall_delta = 0
        self.balance = 0
        self.acceptable_profit = 0.005
        self.binance_percent = 0.001
        self.current_force_wait = 0
        self.max_force_wait = 2
        self._fiat_balance = 0
        self.position = 0

    def get_bounce(self):
        if self.overall_delta < 0.02:
            return self.bounce
        if self.bounce == 0:
            if self.position < 20:
                self.current_bounce = -1
                self.bounce += 1
            if self.position > 80:
                self.current_bounce = 1
                self.bounce += 1
        if self.current_bounce == 1 and self.position < 20:
            self.bounce += 1
            self.current_bounce = -1
        if self.current_bounce == -1 and self.position > 80:
            self.bounce += 1
            self.current_bounce = 1
        return self.bounce

    @property
    def safe_to_trade(self):
        if self.overall_delta < 1.02 and self.high_delta < 1.01 and self.low_delta > .95:
            return True
        return False

    @property
    def current_price(self):
        return self._current_price

    @current_price.setter
    def current_price(self, usd_price):
        self.get_bounce()
        # if self.round > self.reset_rounds:
        #     self.reset()
        self.round += 1
        self.total_price += usd_price
        if self.start_price == 0:
            self.start_price = usd_price
            return
        self.average_price = self.total_price / self.round
        self.beta = self.average_price - usd_price
        self.delta = usd_price / self.start_price
        if self.delta > self.high_delta:
            self.high_delta = self.delta
        if self.delta < self.low_delta:
            self.low_delta = self.delta
        self.overall_delta = self.high_delta - self.low_delta
        self.gamma = self.delta - self.low_delta
        self.alpha = 2.0 - self.low_delta - self.high_delta
        if self.overall_delta > 0:
            self.position = round((self.delta - self.low_delta) / self.overall_delta, 2) * 100

        # _trajectory = 0
        # if (self.delta - 1) < - 0:
        #     _trajectory = -1
        # if (self.delta - 1) > 0:
        #     _trajectory = 1
        # self.bounce.update_trajectory(_trajectory)
        self._current_price = usd_price

    @property
    def fiat_balance(self):
        self._fiat_balance = self.balance * self.current_price
        return self._fiat_balance

    def reset(self):
        self.delta = 1
        self.alpha = 1
        self.round = 0
        self.beta = 0
        self.total_price = 0
        self.average_price = 0
        self.high_delta = -1000
        self.low_delta = 1000
        self.overall_delta = 0
        self.balance = 0
        self.acceptable_profit = 0.005
        self.binance_percent = 0.001
        self.current_force_wait = 0
        self.max_force_wait = 2
        self._fiat_balance = 0
