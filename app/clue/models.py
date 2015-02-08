from app import db
from app.clue import constants as CLUE


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(64), index=True, unique=True)
    clue_id = db.relationship('Clue', backref='category', lazy='dynamic')

    def __repr__(self):
        return '<Category %s>' % self.category


class Answer (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(150), index=True, unique=True)
    clue_id = db.relationship('Clue', backref='answer', lazy='dynamic')

    def __repr__(self):
        return '<Answer %s>' % self.answer


class Value (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, index=True, unique=True)
    clue_id = db.relationship('Clue', backref='value', lazy='dynamic')

    def __repr__(self):
        return '<Value %i>' % self.value


class Episode (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    episode = db.Column(db.Integer, index=True, unique=True)
    clue_id = db.relationship('Clue', backref='episode', lazy='dynamic')

    def __repr__(self):
        return '<Value %i>' % self.episode


class Clue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'))
    value_id = db.Column(db.Integer, db.ForeignKey('value.id'))
    jArchive_episode_id = db.Column(db.Integer, db.ForeignKey('episode.id'))
    clue = db.Column(db.String(650), index=True)
    correct_count = db.Column(db.Integer, default=CLUE.STARTING_VALUE)
    incorrect_count = db.Column(db.Integer, default=CLUE.STARTING_VALUE)

    def __repr__(self):
        return '<Clue %s>' % self.clue