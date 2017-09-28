from cope.authtoken import *
from cope.emailtemplates import *
from cope.db import connect_to_database
from cope import app
from usermodel import get_permition_lookup, get_role_permitions_lookup

import unittest
import jwt

class TestPwt(unittest.TestCase):
    def test_encode_decode(self):
        token = encode_session_token(1)
        payload = decode_session_token(token)
        print(payload)
        self.assertEqual(1, payload.user_id)

    def test_jwt(self):
        payload = ({'user_id': 1})
        token = jwt.encode(payload, app.secret, 'HS256')
        p2 = jwt.decode(token, app.secret, False, 'HS256')
        self.assertEqual(payload, p2)

    def test_jwt_str(self):
        payload = ({'user_id': 1})
        token = jwt.encode(payload, app.secret, 'HS256')
        p2 = jwt.decode(token.decode('utf-8'), app.secret, True, 'HS256')
        self.assertEqual(payload, p2)

    def test_email_body_to_line(self):
        res = email_body_to_line(''' <header>    </header> 
                            <body> </body> ''')
        # print(res)
        self.assertEqual('''<header> </header> <body> </body>''', res)

    def test_get_permition_lookup(self):
        con = connect_to_database()
        permits = get_permition_lookup(con)
        con.close()
        print(permits)
        print(type(permits))

    def test_get_role_permitions_lookup(self):
        con = connect_to_database()
        permits = get_role_permitions_lookup(con)
        con.close()
        print(permits)
        print(type(permits))

# if( __name__ == '__main__'):
#     import sys
#     sys.path.append("/home/pera/projects/cope")
#     unittest.main() 