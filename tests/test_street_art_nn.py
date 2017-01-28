#!flask/bin/python
import os
import tempfile
import pytest

from street_art_nn import street_art_nn


@pytest.fixture
def client(request):
    db_fd, street_art_nn.app.config['DATABASE'] = tempfile.mkstemp()
    street_art_nn.app.config['TESTING'] = True
    client = street_art_nn.app.test_client()
    with street_art_nn.app.app_context():
        street_art_nn.init_db()

    def teardown():
        os.close(db_fd)
        os.unlink(street_art_nn.app.config['DATABASE'])
    request.addfinalizer(teardown)

    return client


def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def test_empty_db(client):
    """Start with a blank database."""
    rv = client.get('/')
    assert b'No entries here so far' in rv.data


def test_login_logout(client):
    """Make sure login and logout works"""
    rv = login(client, street_art_nn.app.config['USERNAME'],
               street_art_nn.app.config['PASSWORD'])
    assert b'You were logged in' in rv.data
    rv = logout(client)
    assert b'You were logged out' in rv.data
    rv = login(client, street_art_nn.app.config['USERNAME'] + 'x',
               street_art_nn.app.config['PASSWORD'])
    assert b'Invalid username' in rv.data
    rv = login(client, street_art_nn.app.config['USERNAME'],
               street_art_nn.app.config['PASSWORD'] + 'x')
    assert b'Invalid password' in rv.data
