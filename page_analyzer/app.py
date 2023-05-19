import os
from flask import (Flask,
                   render_template,
                   redirect,
                   url_for,
                   request,
                   flash,
                   abort)
from psycopg2 import connect, extras, errors

app = Flask(__name__)


@app.get('/')
def root_get():
    return render_template('index.html')
