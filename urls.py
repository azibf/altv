from data import db_session
from flask_ngrok import run_with_ngrok
from data.models import *
from flask import Flask, render_template, redirect, request, abort
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,\
    IntegerField, DateField, TextAreaField,  SelectField, FileField
from wtforms.validators import DataRequired, InputRequired, Length
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from proxmoxer import ProxmoxAPI
from api import *


app = Flask(__name__)
#run_with_ngrok(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    ip = StringField('IP адрес', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class PoolForm(FlaskForm):
    title = StringField('Название пула', validators=[DataRequired()])
    naming = StringField('Паттерн имени ВМ', validators=[DataRequired()])
    golden_img = IntegerField('ID золотого образа', validators=[DataRequired()])
    node = StringField('Узел', validators=[DataRequired()])
    count = IntegerField('Количество', validators=[DataRequired()])
    submit = SubmitField('Готово')


@app.route('/<tit>')
@app.route('/index/<tit>')
def index(tit='Ok'):
    if not current_user:
        return redirect("/login")
    return render_template('base.html', title=tit)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            proxmox = ProxmoxAPI(form.ip.data, user=form.username.data, password=form.password.data, verify_ssl=False, service='PVE')
            session = db_session.create_session()
            user = session.query(User).filter(User.username == form.username.data).filter(User.ip == form.ip.data).filter(User.password == form.password.data).first()
            if user:
                login_user(user, remember=form.remember_me.data)
                return redirect("/main")
            else:
                user = User(
                        username=form.username.data,
                        ip=form.ip.data,
                        password=form.password.data
                        )
                session.add(user)
                session.commit()
            return redirect("/main")
        except:
            return render_template('login.html',
                                message="Ошибка авторизации",
                                form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/pools')
def actiones_list():
    session = db_session.create_session()
    pools = session.query(Pool)
    info = []
    for pool in pools:
        cpu, mem = checkPool(pool.vmids, current_user.ip, current_user.username, current_user.password, pool.node)
        curr = {}
        curr['pool'] = pool
        curr['cpu'] = cpu
        curr['mem'] = mem
        info.append(curr)
    return render_template('pools.html', title='Пулы ВМ', pools=info)


@app.route('/addPool',  methods=['GET', 'POST'])
@login_required
def addPool():
    form = PoolForm()
    vmids=""
    if form.validate_on_submit():
        session = db_session.create_session()
        vmids = create(current_user.ip, current_user.username, current_user.password, form.node.data, form.golden_img.data, form.count.data)
        vmids = ','.join(vmids)
        pool = Pool(
            title=form.title.data,
            count=form.count.data,
            naming=form.naming.data,
            golden_image=form.golden_img.data,
            node=form.node.data,
            vmids=vmids
            )
        try: 
            current_user.pools.append(pool)
            session.merge(current_user)
            session.commit()
            return redirect('/pools')
        except:
            pass
    return render_template('add.html', title='Создание пула',
                           form=form, nodes=nodes(current_user.ip, current_user.username, current_user.password))


@app.route('/editPool/<int:id>', methods=['GET', 'POST'])
@login_required
def editPool(id):
    form = PoolForm()
    session = db_session.create_session()
    pool = session.query(Pool).filter(Pool.id == id).filter(Pool.user == current_user).first()
        
    count = pool.count
    if request.method == "GET":
        if pool:

            form.title.data = pool.title
            form.count.data = pool.count
            form.naming.data = pool.naming
            form.node.data = pool.node
            form.golden_img.data = pool.golden_image
        else:
            abort(404)
    if form.validate_on_submit():
        if pool:
            pool.title = form.title.data
            pool.count = form.count.data
            if pool.count != count:
                vmids = create(current_user.ip, current_user.username, current_user.password, pool.golden_image, pool.count - count)
                pool.vmids = f"{pool.vmids},{','.join(vmids)}"
            session.commit()
            return redirect('/pools')
        else:
            abort(404)
    return render_template('edit.html', title='Редактирование пула', form=form, nodes=nodes(current_user.ip, current_user.username, current_user.password))


@app.route('/pool/<int:id>', methods=['GET', 'POST'])
@login_required
def pool(id):
    session = db_session.create_session()
    pool = session.query(Pool).filter(Pool.id == id).first()
    vm = getPool(pool.vmids, current_user.ip, current_user.username, current_user.password, pool.node)
    return render_template('pool.html', title='Пулы', name=pool.title, vms=vm)


@app.route('/deletePoool/<int:id>', methods=['GET', 'POST'])
@login_required
def deletePool(id):
    session = db_session.create_session()
    pool = session.query(Pool).filter(Pool.id == id).filter(Pool.user == current_user).first()
    if pool:
        session.delete(pool)
        session.commit()
        delete(pool.vmids, current_user.ip, current_user.username, current_user.password, pool.node)
    else:
        abort(404)
    return redirect('/pools')


@app.route('/restartPoool/<int:id>', methods=['GET', 'POST'])
@login_required
def restartPool(id):
    session = db_session.create_session()
    pool = session.query(Pool).filter(Pool.id == id).filter(Pool.user == current_user).first()
    if pool:
        reboot(pool.vmids, current_user.ip, current_user.username, current_user.password, pool.node)
    else:
        abort(404)
    return redirect('/pools')


@app.route('/stopPoool/<int:id>', methods=['GET', 'POST'])
@login_required
def stopPool(id):
    session = db_session.create_session()
    pool = session.query(Pool).filter(Pool.id == id).filter(Pool.user == current_user).first()
    if pool:
        stop(pool.vmids, current_user.ip, current_user.username, current_user.password, pool.node)
    else:
        abort(404)
    return redirect('/pools')


@app.route('/startPoool/<int:id>', methods=['GET', 'POST'])
@login_required
def startPool(id):
    session = db_session.create_session()
    pool = session.query(Pool).filter(Pool.id == id).filter(Pool.user == current_user).first()
    if pool:
        start(pool.vmids, current_user.ip, current_user.username, current_user.password, pool.node)
    else:
        abort(404)
    return redirect('/pools')


@app.route("/main")
def main():
    node = []
    for elem in nodes(current_user.ip, current_user.username, current_user.password):
        item = []
        item.append(elem)
        item.append(int(elem['cpu']/elem['maxcpu']*100))
        item.append(int(elem['mem']/elem['maxmem']*100))
        item.append(int(elem['disk']/elem['maxdisk']*100))
        node.append(item)
    return render_template("index.html", title='Главная', node=node)


if __name__ == '__main__':
    db_session.global_init("db/pool.sqlite")
    app.run(debug=True)