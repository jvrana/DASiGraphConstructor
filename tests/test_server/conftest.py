import os
import tempfile

import pytest
from dasi import create_app
from dasi.database import init_app
from dasi.graphql_schema import schema
from graphene.test import Client
# from cli import App
# with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
#     _data_sql = f.read().decode('utf8')

TESTING = "config.Testing"

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': "sqlite:///" + db_path,
    }, config=TESTING)

    init_app(app)
        # get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

# @pytest.fixture
# def cli():
#     db_fd, db_path = tempfile.mkstemp()
#     cliapp = App(TESTING, {
#         'TESTING': True,
#         'DATABASE': "sqlite:///" + db_path,
#     })
#     cliapp.run(port="8080", thread=True)
#     yield cliapp
#     os.close(db_fd)
#     os.unlink(db_path)

@pytest.fixture
def graphql_client(app):
    return Client(schema)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)