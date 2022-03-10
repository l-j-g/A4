from flask import Blueprint, render_template, session, redirect, url_for
import locale 
from helpers import search_db, get_time

search = Blueprint('search', __name__)
locale.setlocale( locale.LC_ALL, '' )

@search.route('/search/')
@search.route('/search/groupBy=<group>&orderBy=<order>')  
def get_tickers(group='ticker', order='asc'):
    # reset the session variables, set group and order as per the request
    session['group'] = group
    session['order'] = order
    session['page'] = 1
    session['pageKey'] = {}

    response = search_db(group, order, session['page'])
    session['LastEvaluatedKey'] = response.get('LastEvaluatedKey')
    session['pageKey'][session['page']] = response.get('LastEvaluatedKey')
    

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

@search.route('/search/<int:page>')
def get_tickers_page(page):
    try:
        session['page']= page
        response = search_db(session['group'], session['order'], page)
        session['pageKey'][page] = response.get('LastEvaluatedKey')
        #session['LastEvaluatedKey'] = response.get('LastEvaluatedKey')
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
@search.route('/search/next')
def get_next_tickers():

    response=search_db(session['group'], session['order'], session['LastEvaluatedKey'])
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
    