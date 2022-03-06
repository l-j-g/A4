import os
import boto3
import yahoo_fin.stock_info as si
import pandas as pd
import csv 
import datetime
import logging
from boto3.dynamodb.conditions import Key
from threading import Thread
import concurrent.futures

#####################
# V A R I A B L E S #
#####################

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')

if os.environ.get('IS_OFFLINE'):
    dynamodb = boto3.resource('dynamodb', region_name='localhost', endpoint_url='http://localhost:8000')

TICKERS_TABLE = os.environ['TICKERS_TABLE']
table = dynamodb.Table(os.environ['TICKERS_TABLE'])
current_time = datetime.datetime.utcnow().isoformat()

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
def get_time():
    current_time = datetime.datetime.utcnow().isoformat()
    return current_time
def get_info(ticker):
    info = pd.DataFrame.to_dict(si.get_company_info(ticker))
    info = info['Value']
    return info
def get_cash_flow(ticker):
    cash_flow = clean(si.get_cash_flow(ticker))
    return cash_flow
def get_income_statement(ticker):
    income_statement = clean(si.get_income_statement(ticker))
    return income_statement
def get_balance_sheet(ticker):
    balance_sheet = clean(si.get_balance_sheet(ticker))
    return balance_sheet
    

#####################
# F U N C T I O N S #
#####################

def autoUpdate(event, context):

    # Get the last updated entry from the database and return the 'ASX code'.
    response = table.query(
        IndexName = 'LastUpdatedIndex',
        KeyConditionExpression = Key('GSI1PK').eq('TICKERS') & Key('LastUpdated').lt(current_time),
        ScanIndexForward = False,
        Limit = 1
    )
    ticker = response['Items'][0]['ASX code']

    ticker = ticker + '.AX'

    # Get info, cash flow, income statement and balance sheet for the ticker using threading
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor: 
        future_info = executor.submit(get_info, ticker)
        future_cash_flow = executor.submit(get_cash_flow, ticker)
        future_income_statement = executor.submit(get_income_statement, ticker)
        future_balance_sheet = executor.submit(get_balance_sheet, ticker)

    info = future_info.result()
    cash_flow = future_cash_flow.result()
    income_statement = future_income_statement.result()
    balance_sheet = future_balance_sheet.result()

    # Get the last updated entry from the database and return the 'ASX code'.
    response = table.query(
        IndexName = 'LastUpdatedIndex',
        KeyConditionExpression = Key('GSI1PK').eq('TICKERS') & Key('LastUpdated').lt(current_time),
        ScanIndexForward = False,
        Limit = 1
    )
    ticker = response['Items'][0]['ASX code']

    # Update the ticker's summary
    response = table.update_item(
        Key={
            'GSI1PK': 'TICKERS',
            'ASX code': ticker
        },
        UpdateExpression="set #i = :i, #c = :c, #i_s = :i_s, #b_s = :b_s, #LastUpdated = :LastUpdated",
        ExpressionAttributeNames={
            '#i': 'Info',
            '#c': 'Cash Flow',
            '#i_s': 'Income Statement',
            '#b_s': 'Balance Sheet',
            '#LastUpdated': 'LastUpdated'
        },
        ExpressionAttributeValues={
            ':i': info,
            ':c': cash_flow,
            ':i_s': income_statement,
            ':b_s': balance_sheet,
            ':LastUpdated': get_time()
        }
    )
    logger.info("Updated " + ticker + 'at ' + get_time())
    return({"status": "updated"})

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
                'LastUpdated': get_time(),
                'GSI1PK': 'TICKERS'
                }
            )
            logger.info(f"Uploaded {ticker[0]} to the database")

    return({"status": "init success"}) 

