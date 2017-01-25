#!flask/bin/python
import sqlite3
from flask import g, Flask, jsonify

DATABASE = 'art-nn.db'

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
    init_db()
    print('Initialized the database.')


@app.cli.command('import_data')
def import_data():
    print "Importing data from file"
    pass


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    cur = get_db().execute("SELECT * FROM art")
    rv = cur.fetchall()
    cur.close()
    return jsonify({'tasks': rv})


@app.route('/')
def index():
    return "Hello, World!"


if __name__ == '__main__':
    app.run(debug=True)
