from random import shuffle, randint
import time
from threading import Thread
from datetime import datetime
from flask.ext.login import current_user
from flask import render_template, g, session, request, jsonify
from flask.ext.socketio import emit
from sqlalchemy import func, or_, and_
from app import app, socketio, db, thread
from app.clue.models import Category, Clue, Answer


game_category = None
game_clue = None
game_selectable_answers = None
game_answer = None
user_win_amount = dict()
user_wager = dict()
total_difference = 0


def random_category():
    # select random category from category table
    #
    # query with an extra col with random int
    # ->sort
    # ->return first row
    selected_category = Category.query. \
        order_by(func.random()). \
        first()
    return selected_category


def random_selectable_answers(category):
    # collect all possible (distinct) answers ids with specified category from clues table
    possible_answers = db.session.query(Clue.answer_id). \
        filter(Clue.category_id == category.id). \
        distinct(Clue.answer_id). \
        all()

    # shuffle answer ids and return first three
    shuffle(possible_answers)
    selectable_answers_tuple = possible_answers[:3]

    # query and return 3 answers from answer table
    selectable_answers_ids = map(lambda answer_id: answer_id[0], selectable_answers_tuple)
    selectable_answers = Answer.query. \
        filter(or_(Answer.id == selectable_answers_ids[0],
                   Answer.id == selectable_answers_ids[1],
                   Answer.id == selectable_answers_ids[2])). \
        all()
    return selectable_answers


def random_clue(answer, category):
    # query a random clue with specified answer and category IDs
    selected_clue = Clue.query. \
        filter(and_(Clue.answer_id == answer.id,
                    Clue.category_id == category.id)). \
        order_by(func.random()). \
        first()
    return selected_clue


def generate_question():
    global game_category
    global game_selectable_answers
    global game_clue
    global game_answer

    game_category = random_category()
    game_selectable_answers = random_selectable_answers(game_category)
    game_answer = game_selectable_answers[randint(0, 2)]
    game_clue = random_clue(game_answer, game_category)


def emit_page(event, wait_time, msg, target):
    print("emitting " + event)
    socketio.emit(event, msg, namespace=target)
    time.sleep(wait_time)


def game_thread():
    global user_win_amount
    global user_wager
    global total_difference
    while True:
        generate_question()
        user_win_amount.clear()
        user_wager.clear()
        total_difference = 0
        emit_page('next round page',
                  3,
            {},
                  '/_socket')
        emit_page('starting page',
                  3,
                  {'category': game_category.category},
                  '/_socket')
        emit_page('category and value page',
                  10,
                  {'category': game_category.category},
                  '/_socket')
        emit_page('select answer page',
                  10,
                  {'clue': game_clue.clue,
                   'answer1': game_selectable_answers[0].answer,
                   'answer2': game_selectable_answers[1].answer,
                   'answer3': game_selectable_answers[2].answer},
                  '/_socket')
        emit_page('show answer page',
                  3,
                  {'answer': game_answer.answer},
                  '/_socket')
        # produce result table
        emit_page('result page',
                  10,
                  {'total_difference': total_difference},
                  '/_socket')


@app.route('/game')
@app.route('/game/')
@app.route('/game/<option>')
def game(option=None):
    if option == "practice":
        category = random_category()
        selectable_answers = random_selectable_answers(category)
        answer = selectable_answers[randint(0, 2)]
        clue = random_clue(answer, category)
        return render_template('game/game.html',
                               preload={'category': category.category,
                                        'selectable_answers': selectable_answers,
                                        'clue': clue.clue,
                                        'answer': answer.answer},
                               game_script='js/javascript_game.js',
                               mode=option)
    else:
        global thread
        if thread is None:
            generate_question()
            thread = Thread(target=game_thread)
            thread.start()
        if option != "debug" and option != "display":
            option = "socket"
        return render_template('game/game.html',
                               preload=None,
                               game_script='js/socket_game.js',
                               mode=option)


@socketio.on('connect', namespace='/_socket')
def test_connect():
    print('Client connected')


@socketio.on('disconnect', namespace='/_socket')
def test_disconnect():
    print('Client disconnected')


@socketio.on('selected_answer', namespace='/_socket')
def get_user_entered_answer(msg):
    if (msg == '0' or
                '1' == msg or
                msg == '2'):
        selected_answer_index = int(msg)
        selected_answer_id = game_selectable_answers[selected_answer_index].id
        check = selected_answer_id == game_answer.id
        current_amount = 100
        if current_user is not None and current_user.is_authenticated():
            global user_win_amount
            global user_wager
            global total_difference
            current_amount = current_user.money
            if current_user.id in user_win_amount:
                if check:
                    current_user.money = user_win_amount[current_user.id]
                    if current_user.largest_win < user_wager[current_user.id]:
                        current_user.largest_win = user_wager[current_user.id]
                    current_user.correct += 1
                    total_difference += user_wager[current_user.id]
                else:
                    if current_user.largest_loss < user_wager[current_user.id]:
                        current_user.largest_loss = user_wager[current_user.id]
                    current_user.incorrect += 1
                    total_difference -= user_wager[current_user.id]
                print(total_difference)
                db.session.commit()
                user_win_amount.pop(current_user.id)
                user_wager.pop(current_user.id)
        emit('answer response',
             {'check': check,
              'current_amount': current_amount})


@socketio.on('max_wager', namespace='/_socket')
def get_user_max_wager():
    max_wager = 100
    if current_user is not None and current_user.is_authenticated():
        max_wager = current_user.money
    emit('max wager response',
         {'max_wager': max_wager})


@socketio.on('wagered_amount', namespace='/_socket')
def get_user_wager_amount(msg):
    if current_user is not None and current_user.is_authenticated():
        try:
            global user_win_amount
            global user_wager
            current_amount = current_user.money
            wager = int(msg)
            if 0 <= wager <= current_amount and current_user.id not in user_win_amount:
                win_amount = current_amount + wager
                new_money = max(100, current_amount - wager)
                current_user.money = new_money
                db.session.commit()
                user_win_amount[current_user.id] = win_amount
                user_wager[current_user.id] = wager
        except ValueError:
            emit('wager amount response',
                 "Not valid input, please refresh webpage")
            request.namespace.disconnect() #may change to a redirect


@app.route('/_nextQuestion')
def get_question():
    category = random_category()
    selectable_answers = random_selectable_answers(category)
    answer = selectable_answers[randint(0, 2)]
    selectable_answers = map(lambda select: select.answer, selectable_answers)
    clue = random_clue(answer, category)
    return jsonify(category=category.category,
                   selectable_answers=selectable_answers,
                   answer=answer.answer,
                   clue=clue.clue)
