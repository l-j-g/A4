from flask import Blueprint, render_template, request, flash, redirect, url_for 
from helpers import get_item, hover, get_table

ticker = Blueprint('ticker', __name__)

# View to display information about a given ticker

@ticker.route('/ticker/', methods=['GET'])
@ticker.route('/ticker/', methods=['POST']) # Handles POST requests from the search page
@ticker.route('/ticker/<string:ticker>') #  When a ticker is passed in the URL
@ticker.route('/ticker/<string:ticker>/info') #  The 'info' page is the default page
def view_info(ticker=None):
    if request.method == 'POST':
        ticker = request.form['ticker']
    try: # Try to get the ticker from the database
        ticker = ticker.upper()
        response = get_item(ticker)
        # Translate data from db to titles
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
        # Data needed to render the page
        data = {
            'page_title': 'Ticker Details',
            'ticker': response['Item'],
        } 
        return render_template('info.html', page_data=data, headers=headers)
    # If the ticker is not in the database, redirect to the search page
    except:
       # Notify the user that the ticker was not found
       flash('Sorry, we could not find the ticker you requested. Try Again', 'error')
       return redirect('/search')

# View to display cash flow of the ticker
@ticker.route('/ticker/<string:ticker>/cash_flow')
def view_cash_flow(ticker):
    ticker = ticker.upper()
    response = get_item(ticker)
    # Create a HTML table from the data 
    table = get_table(response['Item']['Cash Flow'])

    data ={
        'page_title': 'Cash Flow',
        'ticker': response['Item']
    }

    return render_template('cash_flow.html', page_data=data, table=table)

# View to display balance sheet of the ticker
@ticker.route('/ticker/<string:ticker>/balance_sheet')
def view_balance_sheet(ticker):
    ticker = ticker.upper()
    response = get_item(ticker)
    # Create a HTML table from the data
    table = get_table(response['Item']['Balance Sheet'])
    
    data = {
        'page_title': 'Balance Sheet',
        'ticker': response['Item'],
    }
    return render_template('balance_sheet.html', page_data=data, table=table)

# View to display income statement of the ticker
@ticker.route('/ticker/<string:ticker>/income_statement')
def view_income_statement(ticker):
    ticker = ticker.upper()
    response = get_item(ticker)
    
    table = get_table(response['Item']['Income Statement'])
    
    data = {
        'page_title': 'Income Statement',
        'ticker': response['Item'],
    }
    return render_template('income_statement.html', page_data=data, table=table)