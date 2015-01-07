from app import db
from app.user import constants as USER

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    money = db.Column(db.Integer, default=USER.STARTING_MONEY)
    largest_win = db.Column(db.Integer, default=USER.STARTING_VALUE)
    largest_loss = db.Column(db.Integer, default=USER.STARTING_VALUE)
    last_seen = db.Column(db.DateTime)

    def __repr__(self):
        return '<User %r>' % (self.name)