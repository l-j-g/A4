import os

import boto3
from flask import Flask, jsonify, make_response, render_template, request
from jinja2 import Environment, FileSystemLoader
import yahoo_fin.stock_info as si
import pandas as pd
import csv 




def clean(data):
    data.columns = data.columns.astype(str)
    data = data.fillna(0)
    data = data.astype('float')
    data = data.astype('Int64')
    data = pd.DataFrame.to_dict(data)
    return(data)
    