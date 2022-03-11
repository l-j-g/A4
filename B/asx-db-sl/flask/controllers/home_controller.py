from flask import Blueprint, render_template 

home = Blueprint('home', __name__)

@home.route('/')
def display_homepage():
    data = {
        'page_title': 'Homepage',
    }
    return render_template('home.html', page_data=data)

