from flask import session
from boto3.dynamodb.conditions import Key
import datetime
import pandas as pd
import boto3
import os 


dynamodb = boto3.resource('dynamodb')

# This allows for local testing of the app without having to run the server
if os.environ.get('IS_OFFLINE'):
   # dynamodb_client = boto3.client('dynamodb', region_name='localhost', endpoint_url='http://localhost:8000')
    dynamodb = boto3.resource('dynamodb', region_name='localhost', endpoint_url='http://localhost:8000')

TICKERS_TABLE = os.environ['TICKERS_TABLE']
# Use DynamoDB as a resource 
table = dynamodb.Table(os.environ['TICKERS_TABLE'])
#################
# H E L P E R S #
#################

def search_db(group, order, page, filters=None, limit=25):
    """ Search the table, returning results sorted by the group and order specified. 

    Args:
        sortBy (str): Which Index to get the data from ['LastUpdatedIndex', 'MarketCapIndex', 'ListingDateIndex', 'GroupIndex', 'NameIndex']
        sortOrder (bool): True for Ascending, False for Descending
        limit (int): number of items to return
    """
    # These dictionaries translate user input into the correct format for the query
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
    if page != 1:
        queryDict['ExclusiveStartKey'] = session['pageKey'][f'{int(page)-1}']
    return table.query(**queryDict)

def get_time():
    '''Gets the current time'''
    current_time = datetime.datetime.utcnow().isoformat()
    return current_time

def get_item(ticker):
    ''' Retrieves all avaliable data for a given ticker'''
    response = table.get_item(
       Key={
           'ASX code': ticker
           }
   )
    return(response)

def get_table(data):
    """ Takes a dataframe and returns a styled HTML table. """
    df = pd.DataFrame(data)
    df = df.reindex(columns=sorted(df.columns))

    custom_styles = [
        hover(),
        dict(selector="th", props=[("font-size", "100%"),
                                ("text-align", "left")]),
        dict(selector="caption", props=[("caption-side", "bottom")]),
    ]   
    table = df.style.set_properties(**{'max-width': '500px', 'font-size': '10pt'}) \
        .highlight_null(null_color='red') \
        .set_table_attributes('class="table"') \
        .set_table_styles(custom_styles) \
        .render() 
    return table



def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'red' if val < 0 else 'black'
    return 'color: %s' % color

def hover(hover_color="#ffff99"):
    """Creates hover style for table cells"""
    return dict(selector="tr:hover",
                props=[("background-color", "%s" % hover_color)])