import collections
import psycopg2
from flaskdb import get_db
from db import connect_to_database

__all__ = ('User', 'get_user',  'insert_user', 
            'update_user', 'delete_user', 'delete_user',
            'get_role_permitions_lookup', 'get_permition_lookup',
            'permits', 'rolepermits'
        )

class User():
    def __init__(self):
        self.id = None
        self.email = None
        self.active = None
        self.role = None
        self.first_name = None
        self.last_name = None

def get_user(user_id):
    con = get_db()
    cur = con.cursor()
    cur.execute('''select id, email, active, role_id, first_name, last_name 
                    from app_user where id = %(id)s''', 
                {'id': user_id})
    row = cur.fetchone()
    if(not row):
        return None
    user = User()
    user.id, user.email, user.active, user.role, user.first_name, user.last_name = row
    cur.close()
    return user

def insert_user(user:User, password=None):
    con = get_db()
    cur = con.cursor()
    cur.execute('''insert into app_user values (default, %(email)s, 
            '', %(role)s, %(first_name)s, %(last_name)s, false, now(), now())
            returning id''',
            {'email':user.email, 'role':user.role,
            'first_name':user.first_name, 'last_name':user.last_name}
    )

    row = cur.fetchone()
    if(not row):
        return None

    user_id = row[0]
    if(password):
        cur.execute('''update app_user set pwd_hash = crypt(%(pas)s, gen_salt('bf'))
                        where id = %(id)s
                    ''', {'pas':password, 'id':user_id}
        )  
    cur.close()
    con.commit()
    return user_id


def update_user(user:User):
    con = get_db()
    cur = con.cursor()
    cur.execute('''update app_user 
                        set role= %(role)s,
                        set first_name= %(first_name)s, set first_name= %(first_name)s
                    where id = %(id)sget_role_permitions_lookup
                ''',
            {'id':user.id, 'role':user.role,
            'first_name':user.first_name, 'last_name':user.last_name}
    )
    rowcount  = cur.rowcount

    # TODO this imitates trigger: Introduce trigger and remove this from part
    if(not rowcount):
        cur.close()
        return 0    
    
    cur.execute('update app_user set updated_at = now() where id = %(id)s', {'id':user.id})
    cur.close()
    con.commit()
    return rowcount

def delete_user(user_id:int):
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute('delete from table user_details where id = %(id)s', id=user_id)
        cur.execute('delete from table user  where id = %(id)s', id=user_id)
    except (psycopg2.IntegrityError, psycopg2.DatabaseError) as err:
        con.rollback()    
        cur.close()
        raise err
    rowcount = cur.rowcount
    cur.close()
    return rowcount


def get_role_permitions_lookup(db_conection):
    '''creates role permition lookup named tuple'''
    con = db_conection
    cur = con.cursor()
    cur.execute('select id, permitions from role')
    rpd = {row[0]: int(row[1], 2) for row in cur}    
    cur.close()
    return rpd

def get_permition_lookup(db_conection):
    '''Creates permition lookup named tuple from database enum type positionss
    Called from module to create permition lookup'''
    con = db_conection
    cur = con.cursor()
    cur.execute('SELECT unnest(enum_range(NULL::permition_type))')
    pt = tuple(row[0] for row in cur)    
    cur.close()
    ptyp = collections.namedtuple('permition_lookup', pt)
    return ptyp(*(pow(2, i) for i in range(0, len(pt))))

con = connect_to_database()
permits = get_permition_lookup(con)
rolepermits = get_role_permitions_lookup(con)
con.close()

def generate_password()->str:
    import string
    import secrets 

    alphabet = string.ascii_letters + string.digits
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(10))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and sum(c.isdigit() for c in password) >= 3):
            break    