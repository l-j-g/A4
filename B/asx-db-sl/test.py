import logging
import csv

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



      
with open('../*.csv', newline='') as csvfile:
    tickers_list = csv.reader(csvfile, delimiter=',', quotechar='|')

    headers = next(ticker, None)
    ticker_keys = [key for key in headers]
    print(ticker_keys)
