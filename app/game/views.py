from random import shuffle, randint
import time
from threading import Thread
import functools
from flask import render_template, g, session, request, jsonify
from flask.ext.login import current_user, login_required
from flask.ext.socketio import emit
from sqlalchemy import func, or_, and_
from app import app, socketio, db, thread
from app.clue.models import Category, Clue, Answer


game_category = None
game_clue = None
game_selectable_answers = None
game_answer = None


def random_category():
    # select random category from category table
    #
    # query with an extra col with random int
    # ->sort
    # ->return first row
    selected_category = Category.query.\
                            order_by(func.random()).\
                            first()
    return selected_category


def random_selectable_answers(category):
    # collect all possible (distinct) answers ids with specified category from clues table
    possible_answers = db.session.query(Clue.answer_id).\
        filter(Clue.category_id == category.id).\
        distinct(Clue.answer_id).\
        all()

    # shuffle answer ids and return first three
    shuffle(possible_answers)
    selectable_answers_tuple = possible_answers[:3]

    # query and return 3 answers from answer table
    selectable_answers_ids = map(lambda answer_id: answer_id[0], selectable_answers_tuple)
    selectable_answers = Answer.query.\
        filter(or_(Answer.id == selectable_answers_ids[0],
                   Answer.id == selectable_answers_ids[1],
                   Answer.id == selectable_answers_ids[2])).\
        all()
    return selectable_answers


def random_clue(answer, category):
    # query a random clue with specified answer and category IDs
    selected_clue = Clue.query.\
        filter(and_(Clue.answer_id == answer.id,
                    Clue.category_id == game_category.id)).\
        order_by(func.random()).\
        first()
    return selected_clue


def generate_question():
    global game_category
    global game_selectable_answers
    global game_clue
    global game_answer

    game_category = random_category()
    game_selectable_answers = random_selectable_answers(game_category)
    game_answer = game_selectable_answers[randint(0,2)]
    game_clue = random_clue(game_answer, game_category)


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated():
            request.namespace.disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@app.route('/test/game')
def game_test():
    generate_question()
    return render_template('game/game.html',
                           game_script='js/javascript_game.js')


def emit_page(event, wait_time, msg, target):
    time.sleep(wait_time)
    print("emitting " + event)
    socketio.emit(event, msg, namespace=target)


def game_thread():
    while True:
        generate_question()
        emit_page('starting page',
                  3,
                  {'category': game_category.category},
                  '/_socket')
        emit_page('category and value page',
                  1,
                  {'category': game_category.category},
                  '/_socket')
        emit_page('select answer page',
                  3,
                  {'clue': game_clue.clue,
                   'answer1': game_selectable_answers[0].answer,
                   'answer2': game_selectable_answers[1].answer,
                   'answer3': game_selectable_answers[2].answer},
                  '/_socket')
        emit_page('show answer page',
                  3,
                  {'answer': game_answer.answer},
                  '/_socket')
        #produce result table
        emit_page('result page',
                  3,
                  {},
                  '/_socket')
        emit_page('next round page',
                  2,
                  {},
                  '/_socket')


@app.route('/socket_test/game')
def game():
    global thread
    if thread is None:
        generate_question()
        thread = Thread(target=game_thread)
        thread.start()
    return render_template('game/game.html',
                           game_script='js/socket_game.js')


@socketio.on('connect', namespace='/_socket')
def test_connect():
    print('Client connected')


@socketio.on('disconnect', namespace='/_socket')
def test_disconnect():
    print('Client disconnected')


@socketio.on('selected_answer', namespace='/_socket')
#remove later @authenticated_only
def user_entered_answer(msg):
    if(msg == "0" or
       msg == "1" or
       msg == "2"):
        selected_answer_index = int(msg)
        selected_answer_id = game_selectable_answers[selected_answer_index].id
        emit('answer response',
             {'check': (selected_answer_id == game_answer.id)})
    else:
        print("dropped")



@app.route('/_page0')
def get_page_0():
    generate_question()

@app.route('/_page1')
def get_page_1():
    return jsonify(category=game_category.category)

@app.route('/_page2')
def get_page_2():
    return jsonify(category=game_category.category,
                   clue=game_clue.clue,
                   answer1=game_selectable_answers[0].answer,
                   answer2=game_selectable_answers[1].answer,
                   answer3=game_selectable_answers[2].answer)

@app.route('/_page3')
def get_page_3():
    return jsonify(answer=game_answer.answer)

@app.route('/_page4')
def get_page_4():
    return jsonify(answer=game_answer.answer)


