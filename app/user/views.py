from datetime import datetime
from flask import render_template, flash, redirect, url_for, session, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, lm, oid, db
from app.user.models import User, Email
from app.user.forms import LoginForm, EditForm, SearchForm
from app.user.constants import ROWS_PER_PAGE


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
    g.search_user = SearchForm()


@app.route('/')
@app.route('/index',)
def index():
    user = g.user
    return render_template('index.html',
                           title='Home',
                           user=user)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        print("valid form, trying to login")
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email', 'fullname'])
    return render_template('user/login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


@oid.after_login
def after_login(resp):
    #failed login
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))

    #new user logging in
    email = Email.query.filter_by(email=resp.email).first()
    if email is None:
        print("new user")
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        joined = datetime.utcnow()
        nickname = User.make_valid_nickname(nickname)
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname, joined=joined, full_name=resp.fullname)
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(nickname=nickname).first()
        email = Email(email=resp.email, user_id=user.id)
        db.session.add(email)
        db.session.commit()

    #returning user logging in
    user = email.linked_user
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    print(user)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    return render_template('user/profile.html',
                           user=user)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
    return render_template('user/edit.html', form=form)


@app.route('/leaderboard')
@app.route('/leaderboard/')
@app.route('/leaderboard/<int:page>')
def leaderboard(page=1):
    grabbed_rows = User.query.order_by(User.money.desc()).paginate(page, ROWS_PER_PAGE, False).items
    leaderboard_rows = map(lambda row: {'nickname': row.nickname,
                                        'money': row.money},
                           grabbed_rows)
    for number, row in enumerate(leaderboard_rows):
        row['position'] = (page - 1)*ROWS_PER_PAGE + number + 1
    print(leaderboard_rows)
    return render_template('game/leaderboard.html',
                           leaderboard_rows=leaderboard_rows)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/learn')
def learn():
    return render_template('how-to-play.html')


@app.route('/search', methods=['POST'])
def search():
    if not g.search_user.validate_on_submit():
        flash("Form is not valid, try again")
        return redirect(url_for('index'))
    nickname = g.search_user.data['nickname']
    return redirect(url_for('user', nickname=nickname))
