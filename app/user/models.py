from app import db
import re
from app.user import constants as USER
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.relationship('Email',
                            backref='linked_user',
                            lazy='dynamic')
    nickname = db.Column(db.String(64), index=True, unique=True)
    full_name = db.Column(db.String(64))
    joined = db.Column(db.DateTime, default=datetime.utcnow())
    money = db.Column(db.Integer, default=USER.STARTING_MONEY)
    correct = db.Column(db.Integer, default=USER.STARTING_VALUE)
    incorrect = db.Column(db.Integer, default=USER.STARTING_VALUE)
    largest_win = db.Column(db.Integer, default=USER.STARTING_VALUE)
    largest_loss = db.Column(db.Integer, default=USER.STARTING_VALUE)
    last_seen = db.Column(db.DateTime)
    money_check = db.CheckConstraint('money > 100')


    @staticmethod
    def make_valid_nickname(nickname):
        return re.sub('[^a-zA-Z0-9_\.]', '', nickname)


    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User %s>' % (self.nickname)

class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    email = db.Column(db.String(128), index=True, unique=True)

    def __repr__(self):
        return '<Email %s>' % (self.email)