import os
import flaskr
import unittest
from cope import app

class FlaskrTestCase(unittest.TestCase):


    def setUp(self):
        # self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()

    def test_invite():
        self.app.put()
        pass


    # def tearDown(self):
    #     os.close(self.db_fd)
    #     os.unlink(flaskr.app.config['DATABASE'])

    if __name__ == '__main__':
        unittest.main()