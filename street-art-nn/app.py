#!flask/bin/python
import sqlite3
from flask import g, Flask, jsonify

DATABASE = 'art-nn.db'

app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

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
