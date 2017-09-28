import flask
import psycopg2
import jwt
from api import api, app
from midleware import *
from flaskdb import get_db
from usermodel import *
from validation import *
from authtoken import *
from emailtemplates import *

@api.route('/api/login/', methods = ['GET'])
def login(email:str, password:str):
    '''User login'''
    # email = flask.request.args.get('email')
    # password = str(flask.request.args.get('password'))
    # print(email, password)

    con = get_db()
    cur = con.cursor()
    cur.execute('''select id, (pwd_hash = crypt(%(password)s, pwd_hash)) as pwd_match from app_user 
                    where email = %(email)s''', {'password': password, 'email': email}
              )
    row = cur.fetchone()
    if(row and row[1]): 
        token = encode_session_token(row[0])    
        resp = flask.jsonify({'access_token': token.decode('utf-8')})
    else:
        status = 401
        data = {'mesage':'Invalid password or user name.', 'status':status}
        resp = flask.jsonify(data)
        resp.status = str(status)

    return resp


@api.route('/api/invite/', methods = ['PUT'])
@authorize
@check_permitions(permits.invite) #TODO do not use create perm but create ivite perm 
def invite_user(user_id:int=None):
    ''' Invite user with inviteable permition e.g. manager to register and activate account.
    
    User that has invite permit e.g. user with administrator role can invite manager by email.
    After clicking on link in the email manager creates password by submitting password 
    manager is registered and activated in atomic operation.  
    
    Invite proces sequence diagram
    client                          server                      email
    admin sends invitation
                                    invite_user
                                        sends mail 
                                                                user clicks on link in email
    client reg-act page openss
    client request user from token
                                    get_invited_user_data
                                        server returns user
    client allow usr to create pass
    clinet send regact request      
                                    register_and_activate_manager
                                        server validates request
                                        server activates user
                                        server returns status 
    redirect to login page  #(in this case direct login might be more appropriate)                            
    '''
    # user_id = flask.request.args.get('user_id')
    #validate user
    #although this should work only for manager I will allow it for all

    con = get_db()
    cur = con.cursor()
    cur.execute('''select id, email, active, role_id, first_name, last_name 
                    from app_user where id = %(id)s''', 
                {'id': user_id})
    row = cur.fetchone()
    if(not row):
        return bad_request_400('Invalid user.')

    user = User()
    user.id, user.email, user.active, user.role, user.first_name, user.last_name = row
    if(user.active):
        return flask.jsonify({'msg':'User already activated', 'affected':0})
    
    url = ''  
    if(rolepermits[user.role] & permits.inivteable):
        url = flask.current_app.config['SERVER_NAME'] + '/register-activate' #this is client app path
    else:
        return bad_request_400('Invitation trough web api forbiden.')
    
    #email states and tranitions 
    #pending->dispatched dipatched->sent dispatched->refused

    atoken = encode_email_token(user_id, 'invitation')    
    message= build_invitation_mail_body(url, atoken, user)
    #put email into db   
    sender_email = flask.current_app.config['INVITATION_SENDER']
    cur.execute(
        '''insert into email_queue(id, status, sender, recipient, message, data)
            values(default, 'pending', %(sender)s, %(receiver)s, %(message)s, null)
            returning id
        ''', {'sender':sender_email, 'receiver':user.email, 'message':message}
        )
    id = cur.fetchone()[0]
    cur.close()
    con.commit()
    
    #TODO add mail job into redis queue
    #TODO implement consumer service sender

    return flask.jsonify({'email_queue_id': id})


@api.route('/api/user/invited/', methods = ['GET'])
def get_invited_user(invitation_token:str):
    '''Returns invited user data  
    args: invittion_token obained from invitation email link
    '''
    # invitation_token = flask.request.args.get('invitation_token')
    try:
        payload = decode_email_token(invitation_token, 'invitation')
    except (jwt.DecodeError, jwt.InvalidTokenError) as err:
        print(err)
        return unautorized_exit()

    try:
        user_id = payload['user_id']
    except:
        return unautorized_exit()
    
    user = get_user(user_id)

    if(user is None or user.active):
        return flask.jsonify({})

    return flask.jsonify(vars(user))

@api.route('/api/regact/', methods = ['PATCH'])
def register_and_activate_manager(invitation_token:str, password:str):
    ''' Registration and activation of a user witn invitable permition 
        e.g. user with manager role
    
    Registration - in this case adding password to already created user data
    and
    Activation  - performed upon user confirmation od email
    are one atomic process performed after clicking on manager activation link
    on restricted register page where manager has to create password and cant change his email name
    registration is followed by automatic activation

    manager state tranitons:
    created -> invited (30min)->(registred->activated)
    invited(>30min) -> created
    invited(email refused invald address) -> created     
    '''
    # invitation_token = flask.request.args.get('invitation_token')
    # password = str(flask.request.args.get('password'))

    try:
        payload = decode_email_token(invitation_token, 'invitation')
    except (jwt.DecodeError, jwt.InvalidTokenError) as err:
        print(err)
        return unautorized_exit()    
    
    try:
        user_id = payload['user_id']
    except:
        return unautorized_exit()

    if(not validate_password(password)):
        return bad_request_400('Invalid password')    

    # check if subjected user could be invited e.g. does it have invitable role
    user = get_user(user_id)
    if(user.role != 'manager'):
        return bad_request_400('User can not be invited. Most probably users permition has been changed')

    if(user.active):
        return flask.jsonify({'affected':0, 'msg':'User has already been activated'})

    con = get_db()
    cur = con.cursor()
    # print (password, user_id)
    cur.execute('''update app_user 
            set pwd_hash = crypt(%(pas)s, gen_salt('bf')), active=true, updated_at=now()
            where id = %(id)s and not active
            ''', {'pas':password, 'id':user_id})  

    rowcount  = cur.rowcount
    cur.close()
    con.commit()
    return flask.jsonify({'affected':rowcount})

def send_activation_email(user:User)->int:
    atoken = encode_email_token(user.id, 'activation')
    url = flask.current_app.config['CLIENT_APP_URL'] + '/activate-account'
    message= build_activation_mail_body(url, atoken, user)
    sender_email = flask.current_app.config['ACTIVATION_SENDER']
    
    con = get_db()
    cur = con.cursor()
    cur.execute(
        '''insert into email_queue(id, status, sender, recipient, message, data)
            values(default, 'pending', %(sender)s, %(receiver)s, %(message)s, null)
            returning id
        ''', {'sender':sender_email, 'receiver':user.email, 'message':message}
        )
    id = cur.fetchone()[0]
    cur.close()
    con.commit()
    
    #TODO add mail job into redis queue
    #TODO implement consumer service sender
    return {'email_queue_id': id}

@api.route('/api/register/', methods = ['PUT'])
def register(email:str, password:str, first_name:str=None, last_name:str=None):
    '''User Registration. Applicable to user with register permition e.g. only for user role. 
    User fils personal data form and sends data in order to create account.
    
    Upon storing users data into database email is dispatched to be sent to user in order 
    for useer to confirm his email by clicking on activation link.

    register user proces sequence:   
    client                      server                          email
    guest registers
                                register
                                    validate
                                    inert user into db
                                    (user state: not active)
                                    dispatch activation email
                                                                user(ex guest) click on activation link
    activate page                   
                                activate
                                    validate email token

    redirect to login page      
    '''
    user = User() 
    user.email = email # flask.request.args.get('email')
    # password = email #  flask.request.args.get('password')
    user.first_name = first_name #  flask.request.args.get('first_name')
    user.last_name = last_name #  flask.request.args.get('last_name')
    user.role = 'user'

    print('user.email ', user.email)
    if(not validate_email(user.email)):
        return bad_request_400('Email is not valid')
    if(not validate_password(password)):
        return bad_request_400('Pasword is not valid')
    if(not (rolepermits[user.role] & permits.register)):   #if functionality is changed in future make sure role
        return bad_request_400('Pasword is not valid')
    try:
        id = insert_user(user, password)
    except psycopg2.IntegrityError as err:
        return bad_request_400("User with email '{}' already registered".format(user.email))   
    user.id = id

    try:
        res = send_activation_email(user)
    except (psycopg2.DatabaseError, psycopg2.InterfaceError):
        res = {'error': 'En error occured dispatching email'}

    res['user'] = vars(user)
    return flask.jsonify(res)

@api.route('/api/activate/', methods = ['PATCH'])
def activate_user(activation_token:str):
    ''' User activation 
    user registration->activation state tranitons:
    registered-> created-> pending_activation(<30min)->activated
    registered-> created-> pending_activation(>30min)->created (activation email has to be sent again manually by manager or admin not nedded in spec)

    user creation->registration->activation state tranitons:
    if created by admin user has to be invited the way it is done for manager 
    (this is not covered in specification and it is not implemented here)
    created-> invited (<30min)-> (registred->activated)
    invited(>30min)-> created
    invited(email refused invald address) -> created     
    '''
    # activation_token = flask.request.args.get('activation_token')
    # password = flask.request.args.get('password')

    try:
        payload = decode_email_token(activation_token, 'activation')
    except (jwt.DecodeError, jwt.InvalidTokenError) as err:
        print(err)
        return unautorized_exit()    
    
    try:
        user_id = payload['user_id']
    except:
        return unautorized_exit()
    
    user = get_user(user_id)
    if(user.active):
        return flask.jsonify({'affected':0, 'msg':'User has already been activated'})
    
    #TODO check if subjected user could be a e.g. does it have acivable role
    user = get_user(user_id)
    if(user.role != 'user'):
        return bad_request_400('User can not be invited. Most probably user role has been changed')

    con = get_db()
    cur = con.cursor()
    # print (password, user_id)
    cur.execute('''update app_user set active=true, updated_at=now()
                    where id = %(id)s and not active
            ''', {'id':user_id})  

    rowcount  = cur.rowcount
    cur.close()
    con.commit()
    return flask.jsonify({'affected':rowcount})
