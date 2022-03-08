import pdb
from ast import Expression
import os
import boto3
from flask import Flask, jsonify, make_response, render_template, request, session
import yahoo_fin.stock_info as si
import yfinance as yf
import pandas as pd
import csv 
import json
from decimal import Decimal
from boto3.dynamodb.conditions import Key
import datetime
import locale



app = Flask(__name__)

locale.setlocale( locale.LC_ALL, '' )
SECRET_KEY = os.urandom(12)
app.secret_key = SECRET_KEY
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


@app.route('/search/')
@app.route('/search/groupBy=<group>&orderBy=<order>')  
def get_tickers(group='ticker', order='asc'):
     # Query the table returning the first 25 tickers
    session['LastEvaluatedKey'] = 'NONE' 
    response = search(group, order)
    session['group'] = group
    session['order'] = order
    session['page'] = 1
    session['LastEvaluatedKey'] = response.get('LastEvaluatedKey')

    data = {
        "page_title": "Search Ticker",
        'tickers': response['Items'],
    }

    headers = {
            "ticker": "Tickers",
            "companyName": "Company Name",
            "group": "Category",
            "marketCap": "Market Capitalization",
            "listingDate": "Date Listed"
        }
    
    for key in session:
        print(key, session[key])

    for ticker in data['tickers']:
           ticker['Market Cap'] = locale.currency(ticker['Market Cap'], grouping=True)

    return render_template("ticker_search.html", page_data=data, headers=headers, session=session)

@app.route('/search/next')
def get_next_tickers():

    for key in session:
        print(key, session[key])

    response=search(session['group'], session['order'], session['LastEvaluatedKey'])
    session['LastEvaluatedKey'] = response.get('LastEvaluatedKey')
    session['page'] += 1

    headers = {
            "ticker": "Tickers",
            "companyName": "Company Name",
            "group": "Category",
            "marketCap": "Market Capitalization",
            "listingDate": "Date Listed"
        }

    data = {
        "page_title": "Search Ticker",
        'tickers': response['Items'],
    }

    return render_template("ticker_search.html", page_data=data, headers=headers, session=session)
    

@app.route('/ticker/<string:ticker>')
@app.route('/ticker/<string:ticker>/info')
def view_info(ticker):
   ticker = ticker.upper()
   response = table.get_item(
       Key={
           'ASX code': ticker
           }
   )
  
   print(response)
   headers = {
        "sector": "Sector:", 
        "industry": "Industry:",
        "website": "Website:",
        "address1": "Address:",  
        "city": "City:",
        "state": "State:",
        "phone": "Phone Number:",
        "zip": "Postcode:",
        "country": "Country:",
    } 
   data = {
       'page_title': 'Ticker Details',
       'ticker': response['Item'],
       
   } 

   return(render_template('info.html', page_data=data, headers=headers))

@app.route('/ticker/<string:ticker>/cash_flow')
def view_cash_flow(ticker):
    ticker = ticker.upper()
    response = table.get_item(
        Key={
            'ASX code': ticker
        }
    )
    data = {
        'page_title': 'Cash Flow',
        'ticker': response['Item'],
    }
    return render_template('cash_flow.html', page_data=data)
@app.route('/ticker/<string:ticker>/balance_sheet')
def view_balance_sheet(ticker):
    ticker = ticker.upper()
    response = table.get_item(
        Key={
            'ASX code': ticker
        }
    )
    data = {
        'page_title': 'Balance Sheet',
        'ticker': response['Item'],
    }
    return render_template('balance_sheet.html', page_data=data)
@app.route('/ticker/<string:ticker>/income_statement')
def view_income_statement(ticker):
    ticker = ticker.upper()
    response = table.get_item(
        Key={
            'ASX code': ticker
        }
    )
    data = {
        'page_title': 'Income Statement',
        'ticker': response['Item'],
    }
    return render_template('income_statement.html', page_data=data)

@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)

#################
# H E L P E R S #
#################

def search(group, order, pageKey=None, limit=25):
    """ Function to scan the table and return the data

    Args:
        sortBy (str): Which Index to get the data from ['LastUpdatedIndex', 'MarketCapIndex', 'ListingDateIndex', 'GroupIndex', 'NameIndex']
        sortOrder (bool): True for Ascending, False for Descending
        limit (int): number of items to return
    """
    groupDict = {
        'ticker': 'TickerIndex',
        'marketCap': 'MarketCapIndex',
        'companyName': 'NameIndex',
        'group': 'GroupIndex',
        'listingDate': 'ListingDateIndex'
    }
    orderDict = {
        'asc': True,
        'dsc': False
    }
    queryDict = {
        'IndexName': groupDict[group],
        'KeyConditionExpression': Key('GSI1PK').eq('TICKERS'),
        'ScanIndexForward': orderDict[order],
        'Limit': limit
    }
    print(session)

    if 'LastEvaluatedKey' in session:
        if session['LastEvaluatedKey'] != 'NONE':
            queryDict['ExclusiveStartKey'] = session['LastEvaluatedKey']


    return table.query(**queryDict)

def get_time():
    current_time = datetime.datetime.utcnow().isoformat()
    return current_time

##################################################
# These Functions Are Used for Development only #
#################################################
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
    # Fetch the oldest entry from the database and return the 'ASX code'.


    ticker = '88E.AX'
    info = pd.DataFrame.to_dict(si.get_company_info(ticker))
    info = info['Value']

    return info



@app.route('/init', methods=['POST'])
# initialize the database with basic data from all companies listed on the asx
def init():

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
                print(f"added {ticker[0]} to the database")
            except Exception as e:
                print({
                    header[0]: ticker[0],
                    header[1]: ticker[1],
                    header[2]: ticker[2], 
                    header[3]: ticker[3],
                    header[4]: try_int(ticker[4]),
                    'LastUpdated': datetime.datetime.utcnow().isoformat(),
                    'GSI1PK': 'TICKERS'
                    })
                print(e)
                return("Error")

    return(jsonify({"status": "init success"}))

def try_int(data):
    try:
        data = int(data)
    except:
        data = 0
    return(data)


def clean(data):
    data.columns = data.columns.astype(str)
    data = data.fillna(0)
    data = data.astype('float')
    data = data.astype('Int64')
    data = pd.DataFrame.to_dict(data)
    return(data)