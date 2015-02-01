import os
import unittest

from config import basedir
from app import app, db
from app.user.models import User

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, 'test.db')
        db.create_all()

    def tearDown(self):
        db.drop_all()


    def test_make_unique_nickname(self):
            # create a user and write it to the database
            u = User(nickname='john')
            db.session.add(u)
            db.session.commit()
            nickname = User.make_unique_nickname('john')
            assert nickname != 'john'
            # make another user with the new nickname
            u = User(nickname=nickname)
            db.session.add(u)
            db.session.commit()
            nickname2 = User.make_unique_nickname('john')
            assert nickname2 != 'john'
            assert nickname2 != nickname


if __name__ == '__main__':
    unittest.main()
