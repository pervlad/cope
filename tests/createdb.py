import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

db_name = 'cope'
db_user = 'cope'
db_pass = '123'


def connect_to_database(db_name=db_name, db_user=db_user, db_pass=db_pass):
    return psycopg2.connect("dbname= {} user= {} password={}".format(db_name, db_user, db_pass))

def main():
   # permitions create delete read write read_own

    # admin  create delete read write read_own
    # manger read write read
    # user   read_own
    
# TODO
#     cur.execute('''insert into permition (id, mask) values
#         ('register', b'10000000'), 
#         ('ivite', b'1000000')  ('inivteable', b'100000'), 
#         ('create', b'10000'), ('read', b'01000'),
#         ('edit', b'00010'),  ('read_own', b'00001')
#     ''')
#     cur.execute('create table role (id role_type primary key, permitions bit(8))')
#     cur.execute('''insert into role (id, permitions) values 
#         ('admin', b'001 1111'), ('manager', b'1 0110'), ('user', b'00001')
#     ''')

    con = connect_to_database('template1')
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute('drop database if exists cope')
    cur.execute('create database cope')
    con.close()

    con = connect_to_database()
    cur = con.cursor()

    cur.execute('create extension pgcrypto')
    cur.execute("create type role_type AS ENUM ('admin', 'manager', 'user')")
    cur.execute('''create type permition_type AS ENUM (
                    'read_own', 'read', 'edit', 'delete', 'create', 
                    'register', 'invite', 'inivteable')''')
    cur.execute('create table permition (id permition_type primary key, mask bit(8))')
    cur.execute('''insert into permition (id, mask) values
        ('read_own',    b'00000001'),
        ('read',        b'00000010'),
        ('edit',        b'00000100'),  
        ('delete',      b'00001000'),

        ('create',      b'00010000'),
        ('register',    b'00100000'),
        ('invite',      b'01000000'),
        ('inivteable',  b'10000000')
    ''')
    cur.execute('create table role (id role_type primary key, permitions bit(8))')
    cur.execute('''insert into role (id, permitions) values 
        ('admin', b'01011111'), ('manager', b'10000110'), ('user', b'00100001')
    ''')
    cur.execute('''create table app_user(
        id serial primary key, 
        email varchar unique not null, --could be closer to email syntax but good enough for now 
        pwd_hash varchar(60), 
        role_id role_type references role,
        first_name varchar,
        last_name varchar,
        active boolean not null,
        created_at timestamp default now(),
        updated_at timestamp default now()  
        )
    ''') #TODO add trigger here to avoid unnecessary execution of updates  
    

    # address, phone_number, postal_code, date_ of_birth, gender, avatar(img) created_at, updated_at
    cur.execute('''create table user_details (
        id integer primary key references app_user, 
        address varchar,
        postal_code varchar,
        date_of_birth date,
        avatar_fname varchar,
        created_at timestamp,
        updated_at timestamp)
    ''')

    cur.execute('''insert into app_user values ( default,
        'admin@cope.com', crypt('123', gen_salt('bf')),
        'admin', 'super', 'user', true, now(), now())
        ''')

    cur.execute("create type email_status AS ENUM ('pending', 'dispatched', 'sent', 'refused')")
    
    cur.execute('''create table email_queue(
        id serial, 
        status email_status,
        sender varchar,
        created_at timestamp default now(),
        recipient varchar,
        subject varchar, 
        message text,
        data text
        )
        '''
    )

    cur.close()
    con.commit()
    con.close()

def test():
    con = connect_to_database()
    cur = con.cursor()

    print ('permition lookup:')
    cur.execute('select * from permition')
    for row in cur:
        print(row)

    print ('role lookup:')
    cur.execute('select * from role')
    for row in cur:
        print(row)

    print ('select permitions from role lookup:')
    cur.execute("select permitions from role where id = 'admin'")
    for row in cur: print(row)
    cur.execute("select permitions from role where id = 'manager'")
    for row in cur: print(row)
    cur.execute("select permitions from role where id = 'user'")
    for row in cur: print(row)

    cur.execute('select * from app_user')
    for row in cur:
        print(row)

    cur.execute('''select (pwd_hash = crypt('123', pwd_hash)) as pwd_match, * from app_user 
                    where email = 'pervlad@gmail.com'
                ''')
    for row in cur:
        print (row)

    cur.execute('''select * from app_user 
                    where email = 'pervlad@gmail.com'
                    and (pwd_hash = crypt('123', pwd_hash))
                ''')
    for row in cur:
        print (row)

    cur.execute('''select * from app_user 
                    where email = 'pervlad@gmail.com'
                    and (pwd_hash = crypt('1234', pwd_hash))
                ''')

    if(cur): print('failed')
    for row in cur:
        print(row)

    cur.execute('''select (pwd_hash = crypt(%(password)s, pwd_hash)) as pwd_match
        from app_user 
        where email = %(email)s''', {'password':'123', 'email':'pervlad@gmail.com'})
    row = cur.fetchone()
    print(row)

    cur.execute('''select (pwd_hash = crypt(%(password)s, pwd_hash)) as pwd_match, * from app_user 
                    where email = %(email)s''', {'password':'123', 'email':'xxxxxxx@gmail.com'})
    row = cur.fetchone()
    print(row)

    print('''select id, mask from permition''')
    cur.execute('''select id, mask from permition''')
    for row in cur:
        print(row[0], row[1], bin(int(row[1], 2)), type(row[1]))

    
    cur.close()
    con.close()

    print("psycopg2.apilevel: {}".format(psycopg2.apilevel))
    print("psycopg2.threadsafety: {}".format(psycopg2.threadsafety))
    print("psycopg2.paramstyle: {}".format(psycopg2.paramstyle))

if __name__ == '__main__':
    main()
    # test()
