import os
from os import path

import boto3
from flask import Flask, jsonify, make_response, render_template, request
from jinja2 import Environment, FileSystemLoader

app = Flask(__name__)


dynamodb_client = boto3.client('dynamodb')

if os.environ.get('IS_OFFLINE'):
    dynamodb_client = boto3.client(
        'dynamodb', region_name='localhost', endpoint_url='http://localhost:8000'
    )


TICKERS_TABLE = os.environ['TICKERS_TABLE']
env = Environment(loader=FileSystemLoader(path.join(path.dirname(__file__), 'templates'), encoding='utf8'))

@app.route('/')
def display_homepage():
    data = {
        'page_title': 'Homepage',
    }
    return render_template('home.html', page_data=data)


@app.route('/tickers/<string:ticker>')
def get_user(user_id):
    result = dynamodb_client.get_item(
        TableName=TICKERS_TABLE, Key={'ASX code': {'S': ticker}}
    )
    item = result.get('Item')
    if not item:
        return jsonify({'error': 'Could not find user with provided "ticker"'}), 404

    return jsonify(
        {'ticker': item.get('ASX code').get('S'), 'name': item.get('name').get('S')}
    )


@app.route('/tickers', methods=['POST'])
def create_user():
    ticker = request.json.get('ASX code')
    name = request.json.get('name')
    if not ticker or not name:
        return jsonify({'error': 'Please provide both "ASX code" and "name"'}), 400

    dynamodb_client.put_item(
        TableName=TICKERS_TABLE, Item={'ASX code': {'S': ticker}, 'name': {'S': name}}
    )

    return jsonify({'ticker': ticker, 'name': name})


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
