import logging
import csv

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



      
with open('./ASX_Listed_Companies_24-02-2022_09-03-57_AEDT.csv', newline='') as csvfile:
    tickers_list = csv.DictReader(csvfile, delimiter=',')
    headers = next(tickers_list, None)
    tick_dict = {}
    for ticker in tickers_list:
        print(ticker)

    