import os
import boto3
from flask import Flask, jsonify, make_response, render_template, request
import yahoo_fin.stock_info as si
import yfinance as yf
import pandas as pd
import csv 
import pdb

app = Flask(__name__)


dynamodb_client = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb')

if os.environ.get('IS_OFFLINE'):
    dynamodb_client = boto3.client('dynamodb', region_name='localhost', endpoint_url='http://localhost:8000')
    dynamodb = boto3.resource('dynamodb', region_name='localhost', endpoint_url='http://localhost:8000')


TICKERS_TABLE = os.environ['TICKERS_TABLE']
table = dynamodb.Table(os.environ['TICKERS_TABLE'])

@app.route('/')
def display_homepage():
    data = {
        'page_title': 'Homepage',
    }
    return render_template('home.html', page_data=data)

@app.route('/add/<string:ticker>', methods=['POST'])
def add(ticker):
    ticker = ticker + '.AX'

    values = yf.Ticker(ticker)
    info = values.info
    balance_sheet = values.balance_sheet
    cash_flow = values.cashflow
    income_statement = values.earnings
    ticker = ticker[:-3] 
    print(ticker)
    dynamodb_client.put_item(
        TableName=TICKERS_TABLE, Item={
            'ASX code': ticker,
            'Info': info,
            'Income Statement': income_statement,
            'Cash Flow': cash_flow,
            'Balance Sheet': balance_sheet
        }
    )

    return("hello")

@app.route('/query/<string:ticker>', methods=['POST'])
def query(ticker):

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
            response = table.put_item(
                Item={
                header[0]: ticker[0],
                header[1]: ticker[1],
                header[2]: ticker[2],
                header[3]: ticker[3],
                header[4]: ticker[4]
                }
            )
            print(f"added {ticker[0]} to the database")

    return(jsonify({"status": "init success"}))

@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
