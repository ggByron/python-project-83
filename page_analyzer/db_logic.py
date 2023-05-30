import os
from urllib.parse import urlparse
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from datetime import datetime, date
from validators import url as valid


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def is_valid(url):
    if len(url) < 255 and valid(url) is True:
        return True


def normalize_url(url):
    url = urlparse(url)
    return url._replace(
        path='',
        params='',
        query='',
        fragment='').geturl()


def get_id(url):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM urls WHERE name=%s', (url,))
            id = cur.fetchone()
    conn.close()
    return id if id else None


def add_url(url):
    if get_id(url):
        return None
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO urls (name, created_at)'
                            'VALUES (%s, %s) RETURNING id',
                            (url, datetime.now())
                            )
                id = cur.fetchone()
                return id
    except psycopg2.Error:
        return None
    finally:
        conn.close()


def get_urls():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor
                         ) as nt_cur:
            cur.execute('SELECT urls.id, urls.name, '
                        'url_checks.created_at, url_checks.status_code '
                        'FROM urls LEFT JOIN url_checks '
                        'ON urls.id=url_checks.url_id '
                        'AND url_checks.created_at=(SELECT MAX(created_at) '
                        'FROM url_checks WHERE url_id=urls.id) '
                        'ORDER BY urls.id'
                        )
            rows = nt_cur.fetchall()
    urls = [{'id': row.id,
             'name': row.name,
             'date': row.created_at,
             'status': row.status_code} for row in rows]
    return urls


def find_url(id):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor
                         ) as nt_cur:
            nt_cur.execute('SELECT * FROM urls WHERE id = %s', (id,))
            row = nt_cur.fetchone()
    return {
        'id': row.id,
        'name': row.name,
        'created_at':row.created_at
    }


def add_check(data):
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor
                             ) as nt_cur:
                nt_cur.execute('INSERT INTO url_checks'
                               '(url_id, status_code, h1, title, '
                               'description, created_at)'
                               'VALUES (%s, %s, %s, %s, %s, %s) RETURNING id',
                               (data.get('id'), data.get('code'),
                                data.get('h1'), data.get('title'),
                                data.get('description'),
                                datetime.now())
                               )
                row = nt_cur.fetchone()
                id = row.id

                return id

    except psycopg2.Error:

        return None
    finally:
        conn.close()


def get_checks(id):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor
                         ) as nt_cur:
            nt_cur.execute('SELECT * FROM url_checks '
                           'WHERE url_id=%s ORDER BY id DESC', (id,)
                           )
            rows = nt_cur.fetchall()
    checks = [{'id': row.id,
               'code': row.status_code,
               'h1': row.h1,
               'title': row.title,
               'description': row.description,
               'date': row.created_at} for row in rows]
    conn.close()

    return checks