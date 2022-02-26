import datetime
import logging
import csv
import boto3
import os
from flask import jsonify

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TICKERS_TABLE = os.environ['TICKERS_TABLE']

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

      
    with open('./ASX_Listed_Companies_24-02-2022_09-03-57_AEDT.csv', newline='') as csvfile:
        tickers_list = csv.reader(csvfile, delimiter=',')

        header = next(tickers_list, None)
        #for ticker in tickers_list:
        ticker = next(tickers_list, None) 
        dynamodb_client.put_item(
            TableName=TICKERS_TABLE, Item={
            header[0]: {'S': ticker[0]},
            header[1]: {'S': ticker[1]},
            header[2]: {'S': ticker[2]},
            header[3]: {'S': ticker[3]},
            header[4]: {'S': ticker[4]}
            }
        )
        logger.info("Added ticker: " + ticker[0])

    return(jsonify({"status": "init success"}))