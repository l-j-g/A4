import os

import boto3
from flask import Flask, jsonify, make_response, render_template, request
from jinja2 import Environment, FileSystemLoader
import yahoo_fin.stock_info as si
import pandas as pd
import csv 
import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#################
# H E L P E R S #
#################

def clean(data):
    data.columns = data.columns.astype(str)
    data = data.fillna(0)
    data = data.astype('float')
    data = data.astype('Int64')
    data = pd.DataFrame.to_dict(data)
    return(data)

dynamodb = boto3.resource('dynamodb')

if os.environ.get('IS_OFFLINE'):
    dynamodb = boto3.resource('dynamodb', region_name='localhost', endpoint_url='http://localhost:8000')

TICKERS_TABLE = os.environ['TICKERS_TABLE']
table = dynamodb.Table(os.environ['TICKERS_TABLE'])

def autoUpdate(event, context):

    current_time = datetime.datetime.now().time()

    key = {'ASX code': ticker}
    ticker = ticker + '.AX'
    info = pd.DataFrame.to_dict(si.get_company_info(ticker))
    info = info['Value']

    cash_flow = clean(si.get_cash_flow(ticker))
    income_statement = clean(si.get_income_statement(ticker))
    balance_sheet = clean(si.get_balance_sheet(ticker))
    ticker = ticker[:-3]

    response = table.update_item(
        Key = key,
        UpdateExpression = 'set Info = :i, CashFlow = :c, IncomeStatement = :in, BalanceSheet = :bs',
        ExpressionAttributeValues = {
            ':i': info,
            ':c': cash_flow,
            ':in': income_statement,
            ':bs': balance_sheet,
        }   
    )
    logger.info("Updated " + ticker + ' at' + str(current_time)) 

    return
           
def init(event, context):
    with open('./ASX_Listed_Companies_24-02-2022_09-03-57_AEDT.csv', newline='') as csvfile:
        tickers_list = csv.reader(csvfile, delimiter=',')

        header = next(tickers_list, None)
        for ticker in tickers_list:
            response = table.put_item(
                Item={
                header[0]: ticker[0],
                header[1]: ticker[1],
                header[2]: ticker[2],
                header[3]: ticker[3],
                header[4]: ticker[4],
                'LastUpdated': datetime.datetime.utcnow().isoformat(),
                }
            )

    return(jsonify({"status": "init success"})) 

