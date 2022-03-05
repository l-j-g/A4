import os
import boto3
import yahoo_fin.stock_info as si
import pandas as pd
import csv 
import datetime
import logging
from boto3.dynamodb.conditions import Key

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

    # Get info, cash flow, income statement and balance sheet for the ticker, then update the database.
    ticker = ticker + '.AX'
    info = pd.DataFrame.to_dict(si.get_company_info(ticker))
    info = info['Value']

    cash_flow = clean(si.get_cash_flow(ticker))
    income_statement = clean(si.get_income_statement(ticker))
    balance_sheet = clean(si.get_balance_sheet(ticker))

    ticker = ticker[:-3]
    key = {'ASX code': ticker}
    table.update_item(
        Key = key,
        UpdateExpression = 'set Info = :i, CashFlow = :c, IncomeStatement = :in, BalanceSheet = :bs, LastUpdated = :lu',
        ExpressionAttributeValues = {
            ':i': info,
            ':c': cash_flow,
            ':in': income_statement,
            ':bs': balance_sheet,
            ':lu': get_time()
        }   
    )
    logger.info("Updated " + ticker + ' at' + get_time()) 
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
                'LastUpdated': get_time(),
                'GSI1PK': 'TICKERS'
                }
            )
            logger.info(f"Uploaded {ticker[0]} to the database")

    return({"status": "init success"}) 

