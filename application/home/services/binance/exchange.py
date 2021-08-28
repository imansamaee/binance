from decimal import Decimal

from binance.enums import SIDE_SELL

from application.home.services.binance import API_DATA, logger
from application.home.services.binance.Asset import Asset
from application.home.services.binance.auth import client
from application.home.services.binance.crypto import Crypto


class Exchange:
    def __init__(self, symbol):
        self.symbol_info = Exchange.get_symbol_info(symbol)
        self.symbol = symbol

        self.base_asset_symbol = self.symbol_info['baseAsset']
        self.quote_asset_symbol = self.symbol_info['quoteAsset']
        self.lot_size = next(filter(lambda x: x['filterType'] == 'LOT_SIZE', self.symbol_info['filters']))
        self.min_notional = float(
            next(filter(lambda x: x['filterType'] == 'MIN_NOTIONAL', self.symbol_info['filters']))['minNotional'])
        self.min_qty = float(self.lot_size['minQty'])
        self.max_qty = float(self.lot_size['maxQty'])
        self.step_size = float(self.lot_size['stepSize'])
        self.fees = client.get_trade_fee(symbol=symbol)
        self.side = None

    @staticmethod
    def get_symbol_info(symbol):
        try:
            return next(filter(lambda x: x['symbol'] == symbol, API_DATA.symbols_info))
        except StopIteration:
            print(f"Trade {symbol} not available.")
            return None

    @classmethod
    def check_exchange(cls, symbol1, symbol2):
        if symbol1 == symbol2:
            return False
        trade_symbol = API_DATA.get_trade_symbol(symbol1, symbol2)
        if trade_symbol is not None:
            if trade_symbol not in API_DATA.trade_symbols:
                return False
        return True

    def get_quantity_and_price(self, sell: Crypto, buy: Crypto, trade_symbol, side):
        # print(f"exchange Started!")
        # # trade_symbol = API_DATA.get_trade_symbol(sell.symbol, buy.symbol)
        # print(f"trading {trade_symbol}")
        trade_factor = 1
        trade_price = float(
            next(filter(lambda new_price: new_price['symbol'] == self.symbol, Asset.get_prices_jason()))['price'])

        if side != SIDE_SELL:
            price = trade_price
            trade_factor = trade_price
        else:
            price = 1 / trade_price

        _balance = sell.balance / trade_factor
        _step_size = self.step_size

        _qty = int(_balance / _step_size) * _step_size
        logger.info(f"Sell balance: {sell.balance} Trade symbol: {trade_symbol} step: {_step_size} "
                    f"Trade price: {trade_factor} qty: {_qty}")
        final_qty = round(_qty, abs(Decimal(str(_step_size)).as_tuple().exponent))
        print(f"p: {price} - qty:{final_qty}")
        return {"qty": final_qty, "price": price}


if __name__ == "__main__":
    print(round((1.0119 - 0.9992) / 0.0139, 2) * 100)
