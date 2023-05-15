from flask import Flask, render_template, request


app = Flask(__name__)


@app.get('/')
def root_get():
    return render_template('index.html')
