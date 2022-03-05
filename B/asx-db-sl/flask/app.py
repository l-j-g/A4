from ast import Expression
import os
import boto3
from flask import Flask, jsonify, make_response, render_template, request
import yahoo_fin.stock_info as si
import yfinance as yf
import pandas as pd
import csv 
import json
from decimal import Decimal
from boto3.dynamodb.conditions import Key
import datetime

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


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)

#################
# H E L P E R S #
#################

def get_time():
    current_time = datetime.datetime.utcnow().isoformat()
    return current_time

'''
@app.route('/update/<string:ticker>', methods=['POST'])
def add(ticker):


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
        UpdateExpression = 'set Info = :i, CashFlow = :c, IncomeStatement = :in, BalanceSheet = :bs, LastUpdated = :lu',
        ExpressionAttributeValues = {
            ':i': info,
            ':c': cash_flow,
            ':in': income_statement,
            ':bs': balance_sheet,
            ':lu': datetime.datetime.utcnow().isoformat(),
        }   
    )
    return("OK")

@app.route('/test', methods=['POST'])
def test():
    Fetch the oldest entry from the database and return the 'ASX code'.

    response = table.query(
        IndexName = 'LastUpdatedIndex',
        KeyConditionExpression = Key('GSI1PK').eq('TICKERS'),
        ScanIndexForward = False,
        Limit = 1
    )
    ticker = response['Items'][0]['ASX code']
    return(ticker)

def clean(data):
    data.columns = data.columns.astype(str)
    data = data.fillna(0)
    data = data.astype('float')
    data = data.astype('Int64')
    data = pd.DataFrame.to_dict(data)
    return(data)


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
                header[4]: ticker[4],
                'LastUpdated': datetime.datetime.utcnow().isoformat(),
                'GSI1PK': 'TICKERS'
                }
            )
            print(f"added {ticker[0]} to the database")

    return(jsonify({"status": "init success"}))

'''