import os
import boto3
from flask import Flask, jsonify, make_response, render_template, request, session 
import datetime
import csv

development = True
if development == True:
    import os
    import boto3
    import yahoo_fin.stock_info as si
    import pandas as pd
    import csv 
    import datetime
    import logging
    from boto3.dynamodb.conditions import Key
    from threading import Thread
    import concurrent.futures


# Create an instance of Flask
app = Flask(__name__)

# Set the secret key to some random bytes. 
SECRET_KEY = os.urandom(12)
# Used to store user cookies
app.secret_key = SECRET_KEY

# Register controller to make the code more readable and modular 
from controllers import registerable_controllers
for controller in registerable_controllers:
    app.register_blueprint(controller)

# Routes for basic error handling: 
@app.errorhandler(404)
def handle_404(e):
    return "Error 404: Page not found", 404

@app.errorhandler(500)
def handle_500(e):
    return "Error 500: Internal Server Error", 500
@app.errorhandler(403)
def handle_403(e):
    return "Error 403: Forbidden", 403