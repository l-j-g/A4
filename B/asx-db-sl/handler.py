import datetime
import logging
import csv
import csv
import boto3
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def run(event, context):
    current_time = datetime.datetime.now().time()
    name = context.function_name
    logger.info("Your cron function " + name + " ran at " + str(current_time))


def init(event, context):
    # initialize the database with basic data from all companies listed on the asx
    dynamodb_client = boto3.client('dynamodb')

    if os.environ.get('IS_OFFLINE'):
        dynamodb_client = boto3.client(
            'dynamodb', region_name='localhost', endpoint_url='http://localhost:8000'
        )

    TICKER_TABLE = os.environ['TICKER_TABLE']
      
    with open('../*.csv', newline='') as csvfile:
        tickers_list = csv.reader(csvfile, delimiter=',', quotechar='|')

        headers = next(ticker, None)
        ticker_keys = [key for key in headers]

        for ticker in tickers_list:
            dynamodb_client.put_item(
                TableName=TICKER_TABLE, Key={'ticker': {'S': ticker}}
            )