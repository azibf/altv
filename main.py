from data import db_session
import os
from flask_ngrok import run_with_ngrok
from data.users1 import Actions, User, News, Books, Maps
from flask import Flask, render_template, redirect, request, abort
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,\
    IntegerField, DateField, TextAreaField,  SelectField, FileField
from wtforms.validators import DataRequired, InputRequired, Length
from wtforms.fields.html5 import EmailField
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import requests
import sys


app = Flask(__name__)
run_with_ngrok(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


class SearchForm(FlaskForm):
    groupID = SelectField('Выберите предмет', coerce=str, validators=[InputRequired()])
    submit = SubmitField('Сортировать')

class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Личное")
    submit = SubmitField('Создать')


class BooksForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    author = StringField('Автор')
    subject = StringField('Предмет', validators=[DataRequired()])
    link = StringField('Ссылка', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    ed_level = IntegerField('Класс', validators=[DataRequired()])
    city = StringField('Город', validators=[DataRequired()])
    subject = StringField('Любимые предметы', validators=[DataRequired()])
    vk = StringField('Оставь свой ник в вк, если хочешь, чтобы тебя нашли единомышленнки')
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Проверка пароля', validators=[DataRequired()])
    submit = SubmitField('Зерегистрироваться')


class ActionsForm(FlaskForm):
    title = StringField('Имя', validators=[DataRequired()])
    work_size = IntegerField('Время выполнения', validators=[DataRequired()])
    date = DateField('Дата', validators=[DataRequired()])
    comment = StringField('Комментарий')
    is_finished = BooleanField("Выполнено?")
    submit = SubmitField('Добавить')


@app.route('/<tit>')
@app.route('/index/<tit>')
def index(tit='Ok'):
    return render_template('base.html', title=tit)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/planner")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    logout_user()
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            ed_level=form.ed_level.data,
            city=form.city.data,
            subject=form.subject.data,
            email=form.email.data,
            vk = form.vk.data)
        user.set_password(form.password.data)
        session.add(user)
        for_map = session.query(Maps).filter(Maps.name == form.city.data).first()
        if for_map == None:
            map = Maps(
                name=form.city.data,
                user_counter=1)
            session.add(map)
        else:
            for_map.user_counter += 1
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='register', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/planner')
def actiones_list():
    session = db_session.create_session()
    action = session.query(Actions)
    return render_template('planner.html', title='planner', actions=action)


@app.route('/addaction',  methods=['GET', 'POST'])
@login_required
def add_action():
    form = ActionsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        actions = Actions(
            title=form.title.data,
            work_size=form.work_size.data,
            date=form.date.data,
            comment=form.comment.data,
            is_finished=form.is_finished.data
            )
        current_user.actions.append(actions)
        session.merge(current_user)
        session.commit()
        return redirect('/planner')
    return render_template('actions.html', title='Adding an action',
                           form=form)


@app.route('/addaction/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_action(id):
    form = ActionsForm()
    if request.method == "GET":
        session = db_session.create_session()
        action = session.query(Actions).filter(Actions.id == id).filter(Actions.user == current_user).first()
        if action:
            form.title.data = action.title
            form.work_size.data = action.work_size
            form.comment.data = action.comment
            form.date.data = action.date
            form.is_finished.data = action.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        action = session.query(Actions).filter(Actions.id == id).filter(Actions.user == current_user).first()
        if action:
            action.title = form.title.data
            action.work_size = form.work_size.data
            action.comment = form.comment.data
            action.date = form.date.data
            action.is_finished = form.is_finished.data
            session.commit()
            return redirect('/planner')
        else:
            abort(404)
    return render_template('actions.html', title='Редактирование планов', form=form)


@app.route('/action_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def action_delete(id):
    session = db_session.create_session()
    action = session.query(Actions).filter(Actions.id == id).filter(Actions.user == current_user).first()
    if action:
        session.delete(action)
        session.commit()
    else:
        abort(404)
    return redirect('/planner')


@app.route("/blog")
def blog():
    session = db_session.create_session()
    news = session.query(News).filter(News.is_private != True)
    return render_template("index.html", title='blog', news=news)


@app.route('/addstory',  methods=['GET', 'POST'])
@login_required
def addstory():
    form = NewsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        session.merge(current_user)
        session.commit()
        return redirect('/blog')
    return render_template('news.html', title='Добавление истории',
                           form=form)


@app.route('/story/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_story(id):
    form = NewsForm()
    if request.method == "GET":
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          News.user == current_user).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          News.user == current_user).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            session.commit()
            return redirect('/blog')
        else:
            abort(404)
    return render_template('news.html', title='Редактирование истории', form=form)


@app.route('/story_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def story_delete(id):
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id,
                                      News.user == current_user).first()
    if news:
        session.delete(news)
        session.commit()
    else:
        abort(404)
    return redirect('/blog')


@app.route("/library/<param>", methods=['GET', 'POST'])
def library(param='all'):
    form = SearchForm()
    session = db_session.create_session()
    if param == 'all':
        books = session.query(Books)
    else:
        books = session.query(Books).filter(Books.subject == param)
    session = db_session.create_session()
    available_groups = session.query(Books).all()
    groups_list = [('all', 'Все предметы')]
    for i in available_groups:
        if not ((i.subject, i.subject) in groups_list):
            groups_list.append((i.subject, i.subject))
    groups_list = sorted(groups_list)
    form.groupID.choices = groups_list
    if form.validate_on_submit():
        new = '/library/' + form.groupID.data
        return redirect(new)
    return render_template("library.html", title='library', books=books, form=form)

@app.route('/cheking_book/<int:id>',  methods=['GET', 'POST'])
@login_required
def cheking_book(id):
    session = db_session.create_session()
    books = session.query(Books).filter(Books.id == id).first()
    books.is_checked = True
    session.commit()
    return redirect('/library/all')


@app.route('/addbook/<int:checked>',  methods=['GET', 'POST'])
@login_required
def addbook(checked):
    print(checked)
    form = BooksForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        books = Books()
        books.title = form.title.data
        books.author = form.author.data
        books.subject = form.subject.data
        books.link = form.link.data
        books.is_checked = checked
        session.add(books)
        session.commit()
        return redirect('/library/all')
    return render_template('book.html', title='Добавление книги',
                           form=form)


@app.route('/book/<int:id>', methods=['GET', 'POST'])
@login_required
def book(id):
    form = BooksForm()
    if request.method == "GET":
        session = db_session.create_session()
        books = session.query(Books).filter(Books.id == id).first()
        if books:
            form.title.data = books.title
            form.author.data = books.author
            form.subject.data = books.subject
            form.link.data = books.link
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        books = session.query(Books).filter(Books.id == id).first()
        if books:
            books.title = form.title.data
            books.author = form.author.data
            books.subject = form.subject.data
            books.link = form.link.data
            session.commit()
            return redirect('/library/all')
        else:
            abort(404)
    return render_template('book.html', title='Редактирование книги', form=form)


@app.route('/book_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def book_delete(id):
    session = db_session.create_session()
    books = session.query(Books).filter(Books.id == id).first()
    if books:
        session.delete(books)
        session.commit()
    else:
        abort(404)
    return redirect('/library/all')


def get_coords(elem):
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" + elem \
                       + "&format=json"
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"].split()
        # Печатаем извлечённые из ответа поля:
        return ','.join(toponym_coodrinates)


@app.route("/map", methods=['GET', 'POST'])
def map(param='all'):
    session = db_session.create_session()
    maps = session.query(Maps).all()
    users = session.query(User).filter(User.vk != '')
    coords = []
    for elem in maps:
        if elem.user_counter < 100:
            coords += [get_coords(elem.name) + ",pm2rdm" + str(elem.user_counter)]
        else:
            coords += [get_coords(elem.name) + ",flag"]
    coords = '~'.join(coords)
    map_params = {
        "l": "map",
        "pt": coords
    }
    map_request = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_request, params=map_params)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

        # Запишем полученное изображение в файл.
    map_file = "static/img/map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    return render_template("map.html", title='map', users=users)


if __name__ == '__main__':
    db_session.global_init("db/botay.sqlite")
    app.run()