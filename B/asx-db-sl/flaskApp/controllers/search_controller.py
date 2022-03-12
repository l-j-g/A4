from flask import Blueprint, render_template, session, redirect, url_for
import locale 
from helpers import search_db, get_time 
import simplejson as json
search = Blueprint('search', __name__)
locale.setlocale( locale.LC_ALL, '' )

# View to search for tickers in the database
@search.route('/search/')
@search.route('/search/groupBy=<group>&orderBy=<order>')  
def get_tickers(group='ticker', order='asc'):
    '''
    The sort group and order are passed in the URL. 
    These preferences are stored as cookies (session variables)
    When this route is selected (from the nav bar or any of the table headers) 
    The cookies are reset to the new preferences. 
    '''
    session['group'] = group
    session['order'] = order
    session['page'] = 1
    session['pageKey'] = {}

    response = search_db(group, order, session['page'])

    # Store the pagination key in the session so that pages can be traversed:w
    session['pageKey'][session['page']] = response.get('LastEvaluatedKey')
    
    # Data needed to render the page
    data = {
        "page_title": "Search Ticker",
        'tickers': response['Items'],
    }

    # Convert database names to titles
    headers = {
            "ticker": "Tickers",
            "companyName": "Company Name",
            "group": "Category",
            "marketCap": "Market Capitalization",
            "listingDate": "Date Listed"
        }
    
    # Convert ints into currency format
    for ticker in data['tickers']:
           ticker['Market Cap'] = locale.currency(ticker['Market Cap'], grouping=True)

    return render_template("ticker_search.html", page_data=data, headers=headers, session=session)

@search.route('/search/<string:page>')
def get_tickers_page(page):
    try:
        # Store the current page in the session
        session['page']= int(page)
        # Fetch the next page of results 
        response = search_db(session['group'], session['order'], page)
        # Store the new pagination key in the session
        session['pageKey'][page] = response.get('LastEvaluatedKey')
        # Data needed to render the page
        data = {
            "page_title": "Search Ticker",
            'tickers': response['Items'],
        }

        # Convert database names to titles
        headers = {
                "ticker": "Tickers",
                "companyName": "Company Name",
                "group": "Category",
                "marketCap": "Market Capitalization",
                "listingDate": "Date Listed"
            }
    
        #Convert ints into currency
        for ticker in data['tickers']:
            ticker['Market Cap'] = locale.currency(ticker['Market Cap'], grouping=True)

        return render_template("ticker_search.html", page_data=data, headers=headers, session=session) 
    # If the user doesn't have cookies, redirect to the search page
    except Exception as e:
        print(e)
        return redirect('/search/')

@search.route('/search/<string:page>/filters=<string:query>')
def get_filtered_tickers_page(page):
    try:
        session['page']= int(page)
        response = search_db(session['group'], session['order'], page)
        session['pageKey'][page] = response.get('LastEvaluatedKey')
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
    
        for ticker in data['tickers']:
            ticker['Market Cap'] = locale.currency(ticker['Market Cap'], grouping=True)

        return render_template("ticker_search.html", page_data=data, headers=headers, session=session) 
    except Exception as e:
        print(e)
        return redirect('/search/')
