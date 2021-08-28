from application.home.services.binance.api_data import APIData

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(message)s')

file_handler = logging.FileHandler('binance.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)




API_DATA = APIData()
logger.info("API DATA created.")