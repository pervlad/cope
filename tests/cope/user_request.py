import flask
import psycopg2
from api import api, app
from midleware import *
from flaskdb import get_db
from usermodel import *
from validation import *
from authtoken import *
from usermodel import *


@api.route('/api/user/', methods = ['PUT'])
@authorize
@check_permitions(permits.create)
def create_user(email:str, role:str, first_name:str=None, last_name:str=None):
    '''Creation of user by user who has create permit e.g. adminitrator'''
    user = User()
    user.email = email #flask.request.args.get('email')
    user.role = role #flask.request.args.get('role')
    user.first_name = first_name #flask.request.args.get('first_name')
    user.last_name = last_name #flask.request.args.get('last_name')

    print('email', user.email)
    if(not validate_email(user.email)):
        return bad_request_400('Validation error: invalid email')
    
    if(not validate_role(user.role)):
        return bad_request_400('Validation error: invalid role')    #this is close to asert this is client app responsability

    # pwd = generate_password()
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute('''insert into app_user values (default, %(email)s, 
                '', %(role)s, %(first_name)s, %(last_name)s, false, now(), now())
                returning id''', 
                {'email':user.email, 'role':user.role,
                'first_name':user.first_name, 'last_name':user.last_name}
        )
    except psycopg2.IntegrityError as err:
        return bad_request_400("User with email '{}' already registered".format(user.email))    
    con.commit()
    id = cur.fetchone()[0]
    user.id = id
    return flask.jsonify({'user': vars(user)})


@api.route('/api/user/', methods = ['GET'])
@authorize
@check_permitions(permits.read | permits.read_own)
def get_users(user_id:int=None):
    '''List all users or one user depending on user_id parameter supplied and permitions'''
    perm = flask.g.user.permitions
    # print(bin(perm))
    # print(flask.g.user.id)

    if(user_id is None):
        # all
        if(not(perm & permits.read)):
            return unautorized_exit()    

        con = get_db()
        cur = con.cursor()
        cur.execute('''select id, email, active, role_id as role, first_name, last_name from app_user''')
        columns = cur.description
        res = []
        for value in cur:
            res.append({columns[index][0]:column for index, column in enumerate(value)})
        cur.close()
        return flask.jsonify({'users':res})
    else:
        if((perm & permits.read) or ((perm & permits.read_own) and flask.g.user.id == user_id)):
            user = get_user(user_id)
            return flask.jsonify({'user':vars(user)})
        else:
            return unautorized_exit()


@api.route('/api/user/', methods = ['PATCH'])
@authorize
@check_permitions(permits.edit)
def update_user_req(user_id:int):
    '''Update user of any role permited for user with edit permit e.g. manager and admin roles'''
    affected = update_user(user_id)
    return flask.g.jsonify({'affected':affected})
