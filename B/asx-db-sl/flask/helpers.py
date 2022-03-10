from flask import session
from app import table
from boto3.dynamodb.conditions import Key
import datetime
#################
# H E L P E R S #
#################

def search_db(group, order, page, limit=25):
    """ Search the table, returning results sorted by the group and order specified. 

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
    if page != 1:
        queryDict['ExclusiveStartKey'] = session['pageKey'][f'{int(page)-1}']
    return table.query(**queryDict)

def get_time():
    current_time = datetime.datetime.utcnow().isoformat()
    return current_time

def get_item(ticker):
   response = table.get_item(
       Key={
           'ASX code': ticker
           }
   )
   return(response)
