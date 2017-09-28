import psycopg2

db_name = 'cope'
db_user = 'cope'
db_pass = '123'

def connect_to_database(db_name=db_name, db_user=db_user, db_pass=db_pass):
    return psycopg2.connect("dbname= {} user= {} password={}".format(db_name, db_user, db_pass))