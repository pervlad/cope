__all__ = ('api', 'app') 
import flask
from midleware import bad_request_400
from minirest import Api
from flaskdb import get_db, teardown_db

app = flask.Flask(__name__)
api = Api(app, bad_request_fn = bad_request_400)

app.teardown_appcontext(teardown_db)

