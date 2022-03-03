import os
import boto3
from flask import Flask, jsonify, make_response, render_template, request
import yahoo_fin.stock_info as si
import yfinance as yf
import pandas as pd
import csv 
import json
from decimal import Decimal
import pdb

def clean(dirty_data):
    dirty_data.columns = dirty_data.columns.astype(str)   
    dirty_data = dirty_data.fillna(0)
    print(dirty_data)
    dirty_data = dirty_data.astype('float')
    dirty_data = dirty_data.astype('Int64')
    dirty_data = pd.DataFrame.to_dict(dirty_data)
    clean_data = dirty_data

    return(clean_data) 


    
ticker = '88E'
ticker = ticker + '.AX'

pdb.set_trace()
cash_flow = si.get_cash_flow(ticker)
cash_flow = clean(cash_flow)

income_statement = si.get_income_statement(ticker)
income_statement = clean(income_statement)

balance_sheet = si.get_balance_sheet(ticker)
balance_sheet = clean(balance_sheet)

ticker = ticker[:-3] 
   

        