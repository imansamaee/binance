from application.home.services.binance import logger


class Nominee:
    def __init__(self):
        logger.info("Nominee initiated...")
        self.buy_list = []
        self.best_buy = None
        self.sell = None
        self.last_sell = None
        self.last_buy = None
