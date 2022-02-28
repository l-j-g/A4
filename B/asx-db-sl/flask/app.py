import os

import boto3
from flask import Flask, jsonify, make_response, render_template, request
import yahoo_fin.stock_info as si
import pandas as pd
import csv 

app = Flask(__name__)


dynamodb_client = boto3.client('dynamodb')

if os.environ.get('IS_OFFLINE'):
    dynamodb_client = boto3.client(
        'dynamodb', region_name='localhost', endpoint_url='http://localhost:8000'
    )


TICKERS_TABLE = os.environ['TICKERS_TABLE']

@app.route('/')
def display_homepage():
    data = {
        'page_title': 'Homepage',
    }
    return render_template('home.html', page_data=data)

@app.route('/add_ticker/<string:ticker>', methods=['POST'])
def add_ticker(ticker):
    ticker = ticker + '.AX'

    info = pd.DataFrame.to_json(si.get_company_info(ticker))
    balance_sheet = pd.DataFrame.to_json(si.get_balance_sheet(ticker, False))
    cash_flow = pd.DataFrame.to_json(si.get_cash_flow(ticker, False))
    income_statement = pd.DataFrame.to_json(si.get_income_statement(ticker, False))


    dynamodb_client.put_item(
        TableName=TICKERS_TABLE, Item={
            'ASX code': {'S': ticker},
            'Info' : {'M': info},
            'Income Statement': {'M': income_statement},
            'Cash Flow': {'M': cash_flow},
            'Balance Sheet': {'M': balance_sheet}
        }
    )

@app.route('/query/<string:ticker>', methods=['POST'])
def query(ticker):
    ticker = ticker + '.AX'

    info = pd.DataFrame.to_json(si.get_company_info(ticker))
    balance_sheet = pd.DataFrame.to_json(si.get_balance_sheet(ticker, False))
    cash_flow = pd.DataFrame.to_json(si.get_cash_flow(ticker, False))
    income_statement = pd.DataFrame.to_json(si.get_income_statement(ticker, False))


    response = dynamodb_client.get_item(
        TableName=TICKERS_TABLE, Key={
            'ASX code': {'S': ticker},
        }
    )

    item = response.get('Item')

    if not item:
        return jsonify({'error': 'Could not find any data with provided "ASX code"'}), 404
    return jsonify(item)

@app.route('/init', methods=['POST'])
# initialize the database with basic data from all companies listed on the asx
def init():

    with open('./ASX_Listed_Companies_24-02-2022_09-03-57_AEDT.csv', newline='') as csvfile:
        tickers_list = csv.reader(csvfile, delimiter=',')

        header = next(tickers_list, None)
        for ticker in tickers_list:
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

@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
