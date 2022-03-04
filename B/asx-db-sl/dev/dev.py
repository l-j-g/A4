import os

import boto3
from flask import Flask, jsonify, make_response, render_template, request
from jinja2 import Environment, FileSystemLoader
import yahoo_fin.stock_info as si
import pandas as pd
import csv 
import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def autoUpdate(event, context):
    current_time = datetime.datetime.now().time()
    name = context.function_name
    logger.info("Your cron function " + name + " ran at " + str(current_time)) 

#################
# H E L P E R S #
#################

def clean(data):
    data.columns = data.columns.astype(str)
    data = data.fillna(0)
    data = data.astype('float')
    data = data.astype('Int64')
    data = pd.DataFrame.to_dict(data)
    return(data)

