import datetime
import logging
import csv
import csv
import boto3
import os
import dateutil

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


TICKER_TABLE = os.environ['TICKER_TABLE']
      
with open('../*.csv', newline='') as csvfile:
    tickers_list = csv.reader(csvfile, delimiter=',', quotechar='|')

    headers = next(tickers_list, None)

    for ticker in tickers_list:
        dynamodb_client.put_item(
            TableName=TICKER_TABLE, Key={'ticker': {'S': ticker}}
        )