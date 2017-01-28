#!flask/bin/python
import json
import sqlite3
import os

from geopy.distance import vincenty
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify

DATABASE = 'art_nn.db'

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, DATABASE),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config['JSON_AS_ASCII'] = False
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

@app.route('/artworks/api/v1.0/closest', methods=['GET'])
def get_closest_artworks():
    """ Returns closest artworks to given location

    Should pass lat, lng and limit params with GET request
    If one of them is missing - request will just fail
    """
    lat = float(request.args['lat'])
    lng = float(request.args['lng'])
    limit = int(request.args['limit'])
    artworks_json = _get_all_artworks()

    def distance_km(artwork_from):
        return vincenty((artwork_from["lat"], artwork_from["lng"]), (lat, lng)).km

    def compare_by_distance(artwork1, artwork2):
        distance1 = distance_km(artwork1)
        distance2 = distance_km(artwork2)
        return int(distance1 - distance2)

    sorted_by_distance = sorted(artworks_json, cmp=compare_by_distance)

    return jsonify({'artworks': sorted_by_distance[:limit]})


def _get_all_artworks():
    cur = get_db().execute("SELECT * FROM art")
    rv = cur.fetchall()
    cur.close()
    return [dict(x) for x in rv]


@app.route('/artworks/api/v1.0/artworks', methods=['GET'])
def get_artworks():
    artworks_json = _get_all_artworks()
    return jsonify({'artworks': artworks_json})


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('INSERT INTO art (artist, title, year, image, address, lng, lat) values (?, ?, ?, ?, ?, ?, ?)',
                [request.form["artist"], request.form["title"],
                request.form["year"],
                request.form["image"],
                request.form["address"], request.form["lng"], request.form["lat"]])
    db.commit()
    return redirect(url_for('show_entries'))


@app.route('/delete', methods=['POST'])
def delete_entry():
    if not session.get('logged_in'):
        abort('401')
    db = get_db()
    db.execute('DELETE FROM art WHERE id=?', [request.form["id"]])
    db.commit()
    return redirect(url_for('show_entries'))


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select id, title, artist, image, address from art order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run(debug=True)
