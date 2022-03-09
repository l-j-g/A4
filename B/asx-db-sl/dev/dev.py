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
    try:
        info = pd.DataFrame.to_dict(si.get_company_info(ticker))
        info = info['Value']
    except:
        logger.error(f'Failed to get info for + { ticker }')
        info = "N/A"
    return info
def get_cash_flow(ticker):
    try:
        cash_flow = clean(si.get_cash_flow(ticker))
    except: 
        logger.error(f'Failed to get cash flow for {ticker}')
        cash_flow = "N/A"
    return cash_flow
def get_income_statement(ticker):
    try:
        income_statement = clean(si.get_income_statement(ticker))
    except:
        logger.error(f"Failed to get income statement for {ticker}")
        income_statement = "N/A"
    return income_statement
    
def get_balance_sheet(ticker):
    try:
        balance_sheet = clean(si.get_balance_sheet(ticker))
    except:
        logger.error(f"Failed to get balance sheet for {ticker}")
        balance_sheet = "N/A"
    return balance_sheet
def try_int(data):
    try:
        data = int(data)
    except:
        data = 0
    return(data)

#####################
# F U N C T I O N S #
#####################

def autoUpdate(event, context):

    # Get the last updated entry from the database and return the 'ASX code'.
    response = table.query(
        IndexName = 'LastUpdatedIndex',
        KeyConditionExpression = Key('GSI1PK').eq('TICKERS'), 
        ScanIndexForward = True,
        Limit = 1
    )
    ticker = response['Items'][0]['ASX code']
    ticker = ticker + '.AX'

    # Get info, cash flow, income statement and balance sheet for the ticker using threading
    logger.info(f"Fetching data for {ticker}...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor: 
        future_info = executor.submit(get_info, ticker)
        future_cash_flow = executor.submit(get_cash_flow, ticker)
        future_income_statement = executor.submit(get_income_statement, ticker)
        future_balance_sheet = executor.submit(get_balance_sheet, ticker)

    info = future_info.result()
    cash_flow = future_cash_flow.result()
    income_statement = future_income_statement.result()
    balance_sheet = future_balance_sheet.result()

    ticker = response['Items'][0]['ASX code']

    # Update the ticker's summary
    response = table.update_item(
        Key={
            'ASX code': ticker
        },
        UpdateExpression="set #i = :i, #c = :c, #is = :is, #bs = :bs, #lu = :lu",
        ExpressionAttributeNames={
            '#i': 'Info',
            '#c': 'Cash Flow',
            '#is': 'Income Statement',
            '#bs': 'Balance Sheet',
            '#lu': 'LastUpdated'
        },
        ExpressionAttributeValues={
            ':i': info,
            ':c': cash_flow,
            ':is': income_statement,
            ':bs': balance_sheet,
            ':lu': get_time()
        }
    )
    logger.info("Updated " + ticker + ' at ' + get_time())
    return({"status": "updated"})

def init(event, context):
    
    with open('./ASX_Listed_Companies_24-02-2022_09-03-57_AEDT.csv', newline='') as csvfile:
        tickers_list = csv.reader(csvfile, delimiter=',')

        header = next(tickers_list, None)
        for ticker in tickers_list:
            try:
                response = table.put_item(
                    Item={
                    header[0]: ticker[0] or "N/A",
                    header[1]: ticker[1] or "N/A",
                    header[2]: ticker[2] or "N/A",
                    header[3]: ticker[3] or "N/A",
                    header[4]: try_int(ticker[4]),
                    'LastUpdated': datetime.datetime.utcnow().isoformat(),
                    'GSI1PK': 'TICKERS'
                    }
                )
                logger.info(f"Uploaded {ticker[0]} to the database")
            except Exception as e:
                logger.error(f"Failed to upload {ticker[0]} to the database")
                logger.error(e)
                continue
    return({"status": "initialized"})


