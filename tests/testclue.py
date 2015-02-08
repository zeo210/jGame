import os
import unittest

from config import basedir
from app import app, db
from app.clue.models import Value, Episode, Answer, Category, Clue
from app.clue.add_questions import add_questions

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, 'test.db')
        db.create_all()

    def tearDown(self):
        db.drop_all()


    def test_(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
