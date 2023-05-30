import os
from dotenv import load_dotenv
from flask import (Flask, render_template, url_for,
                   redirect, request, flash, get_flashed_messages
                   )
import page_analyzer.db_logic as db
import requests


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.get('/')
def root_get():
    return render_template('index.html')


@app.get('/urls')
def urls_get():
    urls = db.get_urls()
    return render_template('urls.html', urls=urls)


@app.post('/urls')
def urls_post():
    input = request.form.to_dict()
    url = input['url']

    if not db.is_valid(url):
        flash('Некорректный URL', 'alert-danger')
        msgs = get_flashed_messages(with_categories=True)
        return render_template('index.html', url=url, msgs=msgs), 422

    url = db.normalize_url(url)
    if db.get_id(url):
        id = db.get_id(url)
        flash('Страница уже существует', 'alert-info')
        return redirect(url_for('url_get', id=id))

    id = db.add_url(url)
    if id is None:
        flash('Something wrong', 'alert-danger')
        msgs = get_flashed_messages(with_categories=True)
        return render_template('index.html', url=url, msgs=msgs), 422

    flash('Страница успешно добавлена', 'alert-success')
    return redirect(url_for('url_get', id=id))


@app.get('/urls/<int:id>')
def url_get(id):
    url = db.find_url(id)
    msgs = get_flashed_messages(with_categories=True)
    return render_template('url.html', url=url, msgs=msgs)
