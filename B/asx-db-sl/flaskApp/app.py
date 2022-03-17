import os
import boto3
from flask import Flask, jsonify, make_response, render_template, request, session, send_from_directory
import datetime
import csv 

development = False

# Create an instance of Flask
app = Flask(__name__)

# Set the secret key to some random bytes. 
SECRET_KEY = os.urandom(12)
# Used to store user cookies
app.secret_key = SECRET_KEY

# Register controller to make the code more readable and modular 
from controllers import registerable_controllers
for controller in registerable_controllers:
    app.register_blueprint(controller)

# Routes for basic error handling: 
@app.errorhandler(404)
def handle_404(e):
    return "Error 404: Page not found", 404

@app.errorhandler(500)
def handle_500(e):
    return "Error 500: Internal Server Error", 500
@app.errorhandler(403)
def handle_403(e):
    return "Error 403: Forbidden", 403

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if development: 
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
    from helpers import table


    #######################################################
    # These Functions Are Used for Local Development only #
    #######################################################
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
                ':lu': datetime.datetime.utcnow().isoformat()
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