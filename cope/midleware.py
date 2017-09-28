import flask
import functools
import jwt
from authtoken import decode_session_token
from flaskdb import get_db
from usermodel import User

__all__ = ('unautorized_exit', 'bad_request_400', 'authorize', 'check_permitions')

def unautorized_exit():
    status = 401
    resp = flask.jsonify({})
    resp.status = 'Unautorized access'
    resp.status_code = status
    return resp

def bad_request_400(reason:str):
    status = 400
    resp = flask.jsonify({'mesage':reason})
    resp.status = reason
    resp.status_code = status
    return resp


def authorize(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        token = flask.request.headers.get('Authorization')
        try:
            payload = decode_session_token(token)
        except (jwt.DecodeError, jwt.InvalidTokenError) as err:
            print(err)
            return unautorized_exit()

        con = get_db()
        cur = con.cursor()
        cur.execute('select id, email, active, role_id from app_user where id = %(id)s', 
                    {'id': payload['user_id']})
        row = cur.fetchone()
        if(row):
            user = User()
            user.id, user.email, user.active, user.role = row
            if(user.active):
                flask.g.user = user
                return func(*args, **kwargs)
        return unautorized_exit()
    return wrap


def check_permitions(required_permitions:int):
    '''In time domain this decorator has to be called after authorize decorator.
    '''
    def inner_dec(func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            user = getattr(flask.g, 'user', None)
            assert(user is not None)
            # print('user ', user)
            con = get_db()
            cur = con.cursor()
            cur.execute('select permitions from role where id = %(id)s', {'id': user.role})
            row = cur.fetchone()
            assert row is not None
            user.permitions = int(row[0], 2)
            if (required_permitions & user.permitions):
                return func(*args, **kwargs)
            else:
                return unautorized_exit()
        return wrap
    return  inner_dec 