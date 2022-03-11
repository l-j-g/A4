from flask import Blueprint, render_template, request, flash, redirect, url_for 
from helpers import get_item, hover, get_table
import pandas as pd

ticker = Blueprint('ticker', __name__)


@ticker.route('/ticker/', methods=['POST'])
@ticker.route('/ticker/<string:ticker>')
@ticker.route('/ticker/<string:ticker>/info')
def view_info(ticker=None):
    if request.method == 'POST':
        ticker = request.form['ticker']
       
    ticker = ticker.upper()
    try: 
        response = get_item(ticker)
  
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
        return render_template('info.html', page_data=data, headers=headers)
    except:
       flash('Sorry, we could not find the ticker you requested. Try Again', 'error')
       return redirect('/search')

@ticker.route('/ticker/<string:ticker>/cash_flow')
def view_cash_flow(ticker):
    ticker = ticker.upper()
    response = get_item(ticker)
    table = get_table(response['Item']['Cash Flow'])

    data ={
        'page_title': 'Cash Flow',
        'ticker': response['Item']
    }

    return render_template('cash_flow.html', page_data=data, table=table)

@ticker.route('/ticker/<string:ticker>/balance_sheet')
def view_balance_sheet(ticker):
    ticker = ticker.upper()
    response = get_item(ticker)
    table = get_table(response['Item']['Balance Sheet'])
    
    data = {
        'page_title': 'Balance Sheet',
        'ticker': response['Item'],
    }
    return render_template('balance_sheet.html', page_data=data, table=table)

@ticker.route('/ticker/<string:ticker>/income_statement')
def view_income_statement(ticker):
    ticker = ticker.upper()
    response = get_item(ticker)
    table = get_table(response['Item']['Income tatement'])
    

    data = {
        'page_title': 'Income Statement',
        'ticker': response['Item'],
    }
    return render_template('income_statement.html', page_data=data, table=table)