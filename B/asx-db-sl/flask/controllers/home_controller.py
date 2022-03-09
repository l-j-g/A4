from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from app import table

home = Blueprint('home', __name__)

@home.route('/')
def display_homepage():
    data = {
        'page_title': 'Homepage',
    }
    return render_template('home.html', page_data=data)

