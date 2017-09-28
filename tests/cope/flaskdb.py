import flask
from db import connect_to_database

def get_db():
    db = getattr(flask.g, '_db', None)
    if db is None:
        db = flask.g._db = connect_to_database()
    return db

def teardown_db(exception):
    db = getattr(flask.g, '_db', None)
    if db is not None:
        db.close()