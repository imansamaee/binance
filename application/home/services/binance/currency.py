from currency_converter import CurrencyConverter


class Currency:
    def __init__(self, usd_value):
        self.currencyConverter = CurrencyConverter()
        self.USD = usd_value
        self.USD_round = round(usd_value, 2)
        self.AUD = self.currencyConverter.convert(usd_value, "USD", "AUD")
        self.AUD_round = round(self.AUD, 2)

# print(c.convert(100, 'AUD','USD'))
