#!flask/bin/python
import json
import sqlite3
import os
from flask import g, Flask, jsonify

DATABASE = 'art_nn.db'

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, DATABASE),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('STREET_ART_SETTINGS', silent=True)


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    print('Starting db init')
    init_db()
    print('Initialized the database.')


@app.cli.command('import_data')
def import_data():
    filename = os.path.join(os.path.dirname(__file__), '../util/data.json')
    with open(filename) as f:
        data = json.load(f)
        db = get_db()
        rows = []
        for artwork in data:
            try:
                rows.append([artwork["artist"], artwork["name"], artwork["year"], artwork["image"],
                                artwork["location"]["address"],
                                artwork["location"]["lng"],
                                artwork["location"]["lat"]])
            except:
                # That's probably ok to ignore data errors here
                continue
        for row in rows:
            db.execute('INSERT INTO art (artist, title, year, image, address, lng, lat) values (?, ?, ?, ?, ?, ?, ?)',
                        row)
        db.commit()


@app.cli.command('add_test_data')
def add_test_data():
    db = get_db()
    db.execute('INSERT INTO art (artist, title, year, image, address, lng, lat) values ("artist", "title", "year", "image", "address", 24.54, 24.54)')
    db.commit()


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/artworks/api/v1.0/artworks', methods=['GET'])
def get_tasks():
    cur = get_db().execute("SELECT * FROM art")
    rv = cur.fetchall()
    cur.close()
    artworks_json = [dict(x) for x in rv]
    return jsonify({'artworks': artworks_json})


@app.route('/')
def index():
    return "Hello, World!"


if __name__ == '__main__':
    app.run(debug=True)
