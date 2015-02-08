from app import db, basedir
from app.clue.models import Episode, Value, Category, Answer, Clue
import csv
import os


def replacing_normalize(string):
    return string.decode('utf8').encode('ascii', errors='xmlcharrefreplace')

def add_questions(target):
    with open(target) as open_csv_file:
        csv_reader = csv.reader(open_csv_file)
        next(csv_reader)
        count = 0
        for row in csv_reader:
            print(row)

            episode = Episode.query.filter_by(episode=int(row[0])).first()
            if episode is None:
                episode = Episode(episode=int(row[0]))
                db.session.add(episode)
                db.session.commit()
                Episode.query.filter_by(episode=int(row[0])).first()

            normalized_category = replacing_normalize(row[1])
            category = Category.query.filter_by(category=normalized_category).first()
            if category is None:
                category = Category(category=normalized_category)
                db.session.add(category)
                db.session.commit()
                category = Category.query.filter_by(category=normalized_category).first()

            value = Value.query.filter_by(value=int(row[2])).first()
            if value is None:
                value = Value(value=int(row[2]))
                db.session.add(value)
                db.session.commit()
                value = Value.query.filter_by(value=int(row[2])).first()

            normalized_answer = replacing_normalize(row[4])
            answer = Answer.query.filter_by(answer=normalized_answer).first()
            if answer is None:
                answer = Answer(answer=normalized_answer)
                db.session.add(answer)
                db.session.commit()
                answer = Answer.query.filter_by(answer=normalized_answer).first()

            normalized_clue = replacing_normalize(row[3])
            clue = Clue.query.\
                filter_by(clue=normalized_clue, category=category, answer=answer).\
                first()
            if clue is None:
                clue = Clue(episode=episode,
                            category=category,
                            value=value,
                            answer=answer,
                            clue=normalized_clue)
                db.session.add(clue)
                db.session.commit()

if __name__ == '__main__':
    add_questions(os.path.join(basedir, *['app','clue','clues.csv']))
