import logging
import csv
import yfinance as yf
import yahoo_fin.stock_info as si
import pandas as pd
import pprint

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



      
with open('./ASX_Listed_Companies_24-02-2022_09-03-57_AEDT.csv', newline='') as csvfile:
    tickers_list = csv.DictReader(csvfile, delimiter=',')
    tickers_list = csv.reader(csvfile, delimiter=',')
    headers = next(tickers_list, None)
    tick_dict = {}
    TickersTables = []
    ticker_name = '88E.AX'

    info = si.get_company_info(ticker_name)
    balance_sheet = si.get_balance_sheet(ticker_name, False)
    cash_flow = si.get_cash_flow(ticker_name, False)
    income_statement = si.get_income_statement(ticker_name, False)
    print(balance_sheet)
    x = (pd.DataFrame.to_json(balance_sheet))
    print(x)