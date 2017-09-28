import flask
import psycopg2
import jwt
import datetime
import functools
import collections

import minirest
from authtoken import *
from db import connect_to_database
from flaskdb import get_db
from usermodel import *
from validation import *
from emailtemplates import *
from midleware import *

import registration_requests
import user_request

from api import app, api

email_secret = 'hfuh?38'
email_delta = 60*30
secret = '8i29gr9!n_notgenerated'
expdelta = 60*60


#BL tokens
encode_session_token.secret = secret
encode_session_token.expdelta = expdelta

decode_session_token.secret = secret
decode_session_token.expdelta = expdelta

encode_email_token.secret = email_secret
encode_email_token.expdelta = email_delta

decode_email_token.secret = email_secret
decode_email_token.expdelta = email_delta


api.route(api.document_route, methods=['GET']) (
## uncoment to unleash auth
# authorize(
# check_permitions(permits.create)(
api.get_doc_json_req)
# ))


@api.route('/api/debug/emails', methods = ['GET'])
@authorize
@check_permitions(permits.create)
def email_queue(email_id:int=None):
    '''List email queue to bypass email service functionality'''  

    con = get_db()
    cur = con.cursor()
    cur.execute('''select * from email_queue order by id desc''')
    columns = cur.description
    res = []
    for value in cur:
        res.append({columns[index][0]:column for index, column in enumerate(value)})
    cur.close()
    return flask.jsonify({'email_queue':res})


if __name__ == '__main__':
    api.debug = True
    app.config['INVITATION_SENDER'] = 'support@cope.net'    
    app.config['ACTIVATION_SENDER'] = 'support@cope.net'
    app.config['CLIENT_APP_URL'] = 'localhost:5555'
    app.config['SERVER_NAME'] = 'localhost:5000'
    app.run(debug=True)
    # app.run()
   
   