from flask import render_template, flash, redirect, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from forms import *
from __init__ import app, db

current_id = int()


@app.before_request
def before_request():
    g.user = current_user
    g.id = current_id


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data.lower()).first()
        if user is None:
            flash("No user with such nickname")
        elif form.password.data == user.password:
            login_user(user)
            global current_id
            current_id = user.id
            return redirect(request.args.get('next') or url_for('find'))
        else:
            flash('Wrong password')
    return render_template('login.html', title='Sign In', form=form,
                           Storage=Storage, Client=Client, Operation=Operation, Ware=Ware, User=User,
                           WareStorage=WareStorage, WareOperation=WareOperation,
                           ROLE_USER=ROLE_USER, ROLE_ADMIN=ROLE_ADMIN)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    global current_id
    current_id = None
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.login.data.lower()).first()
        if user is None:
            role = ROLE_USER
            if form.special_password.data == ADMIN_PASSWORD:
                role = ROLE_ADMIN
            if form.special_password.data and role == ROLE_USER:
                flash('WRONG SPECIAL PASSWORD')
                return redirect(url_for('register'))
            user = User(nickname=form.login.data.lower(), email=form.email.data.lower(),
                        password=form.password.data, role=role.lower())
            db.session.add(user)
            db.session.commit()
            flash('Registred succesfully')
            return redirect(request.args.get('next') or url_for('index'))
        flash('User with this nickname already exist')
    return render_template("register.html", form=form,
                           Storage=Storage, Client=Client, Operation=Operation, Ware=Ware, User=User,
                           WareStorage=WareStorage, WareOperation=WareOperation,
                           ROLE_ADMIN=ROLE_ADMIN, ROLE_USER=ROLE_USER)


@app.route('/', methods=['GET', 'POST'])
def index():
    if g.id and g.user is not None and g.user.is_authenticated:
        return render_template("user_base_page.html", user_id=g.id,
                               Ware=Ware, Storage=Storage, Operation=Operation, Client=Client, User=User,
                               WareStorage=WareStorage, WareOperation=WareOperation,
                               ROLE_ADMIN=ROLE_ADMIN, ROLE_USER=ROLE_USER)
    else:
        flash("You must be logged in to access this page")
        return redirect(url_for('login'))


@login_required
@app.route('/new_operation')
def new_operation():
    form = NewOperationForm()
    if form.validate_on_submit():
        form.create_instance()
        flash("Added new request")
        return redirect(url_for("index"))
    return render_template("new_operation.html", form=form, user_id=g.id,
                           Ware=Ware, Storage=Storage, Operation=Operation, Client=Client, User=User,
                           WareStorage=WareStorage, WareOperation=WareOperation,
                           ROLE_ADMIN=ROLE_ADMIN, ROLE_USER=ROLE_USER)


@login_required
@app.route('/handle_request')
def handle_request():
    form = HandleRequestForm()
    _request = sorted(Operation.query.filter_by(handled=0), key=lambda _: _.date_time)[0]
    if form.validate_on_submit():
        for i in range(len(form.inputs)):
            s = Storage.query.get(int(form.inputs[i].data))
            stw = WareStorage.query.filter_by(storage_id=int(form.inputs[i].data), ware_id=_request.ware_op[i].ware_id)
            if not stw:
                stw = WareStorage(ware_id=_request.ware_op[i].ware_id, ware_count=_request.ware_op[i].ware_count,
                                  storage_id=int(form.inputs[i].data))
            else:
                stw.ware_count = stw.ware_count + (1 if _request.ware_op[i].operation_type == "завоз" else -1) * \
                                 _request.ware_op[i].ware_count
            s.st_ware.append(stw)
            db.session.add(s)
            db.session.add(stw)
        _request.handled = 1
        db.session.add(_request)
        db.session.commit()
    return render_template("handle_request.html", form=form,
                           request=_request, user_id=g.id,
                           Ware=Ware, Storage=Storage, Operation=Operation, Client=Client, User=User,
                           WareStorage=WareStorage, WareOperation=WareOperation,
                           ROLE_ADMIN=ROLE_ADMIN, ROLE_USER=ROLE_USER)


@app.route('/storage_info/<_id>')
def storage_info(_id):
    form = StorageInfoForm()
    if form.validate_on_submit():
        form.create_instance(_id)
        return redirect(url_for('storage_info'))
    return render_template("storage_info.html", form=form, user_id=g.id, st_id=_id,
                           Ware=Ware, Storage=Storage, Operation=Operation, Client=Client, User=User,
                           WareStorage=WareStorage, WareOperation=WareOperation,
                           ROLE_ADMIN=ROLE_ADMIN, ROLE_USER=ROLE_USER)


@app.route('/storage_ware')
def storage_ware(st_id=None, w_id=None, ware_count=None):
    if st_id is not None and w_id is not None and ware_count is not None:
        ws = WareStorage.query.filter_by(storage_id=st_id, ware_id=w_id).first()
        if ws:
            if ws.ware_count >= ware_count:
                ws.ware_count -= ware_count
            db.session.add(ws)
            db.session.commit()
            flash("Disposed ware_id:{} from storage_id:{} in count of {}".format(w_id, st_id, ware_count))
            return redirect(url_for("storage_ware"))
        raise Exception(
            "Trying to remove from empty ware_id:{} from storage_id:{} in count of {}".format(w_id, st_id, ware_count))
    return render_template("storage_ware.html", user_id=g.id,
                           Ware=Ware, Storage=Storage, Operation=Operation, Client=Client, User=User,
                           WareStorage=WareStorage, WareOperation=WareOperation,
                           ROLE_ADMIN=ROLE_ADMIN, ROLE_USER=ROLE_USER)


@app.route('/client_info')
def client_info():
    return render_template("client_info.html", user_id=g.id,
                           Ware=Ware, Storage=Storage, Operation=Operation, Client=Client, User=User,
                           WareStorage=WareStorage, WareOperation=WareOperation,
                           ROLE_ADMIN=ROLE_ADMIN, ROLE_USER=ROLE_USER)


def Clear_DB():
    for t in [Client, Storage, Operation, Ware, WareOperation]:
        for t1 in t.query.all():
            db.session.delete(t1)
    db.session.commit()


def Print_DB():
    for t in [Client, Storage, Operation, Ware, WareOperation]:
        yield t.query.all()


if __name__ == '__main__':
    # Clear_DB()
    for x in list(Print_DB()):
        print(x)
    app.run(debug=True)
