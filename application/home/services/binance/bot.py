import json

from application.home.services.binance import logger
from application.home.services.binance.trade import Trade


class TradeBot:
    def __init__(self):
        logger.info("Bot Started...")
        self.trade = Trade()

    def to_json(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__,
                                     sort_keys=True, indent=4))
