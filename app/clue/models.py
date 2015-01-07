from app import db
from app.clue import constants as CLUE

class Clue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('Category.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('Answer.id'))
    value_id = db.Column(db.Integer, db.ForeignKey('Value.id'))
    clue = db.Column(db.String(128), index=True)
    correct_count = db.Column(db.Integer, default=CLUE.STARTING_VALUE)
    incorrect_count = db.Column(db.Integer, default=CLUE.STARTING_VALUE)
    j_archive_game_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Clue %r>' % (self.clue)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return '<Category %r>' % (self.name)

class Answer (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return '<Answer %r>' % (self.answer)

class Value (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return '<Value %r>' % (self.value)