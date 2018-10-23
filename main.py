from flask import render_template, flash, redirect, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from forms import *
from __init__ import app, db

current_id = None


@app.before_request
def before_request():
    g.user = current_user
    g.id = 0 if not g.user.is_authenticated else g.user.id


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
            return redirect(request.args.get('next') or url_for('index'))
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
        user = User.query.filter_by(login=form.login.data.lower()).first()
        if user is None:
            role = ROLE_USER
            if form.special_password.data == ADMIN_PASSWORD:
                role = ROLE_ADMIN
            if form.special_password.data and role == ROLE_USER:
                flash('WRONG SPECIAL PASSWORD')
                return redirect(url_for('register'))
            user = User(login=form.login.data.lower(), password=form.password.data, role=role)
            db.session.add(user)
            if user.role == ROLE_USER:
                c = Client(name=form.name.data.lower(),
                           user_id=User.query.filter_by(
                               login=form.login.data.lower(), password=form.password.data, role=role
                           ).first().id)
                db.session.add(c)
                db.session.commit()
            flash('Registred succesfully')
            return redirect(request.args.get('next') or url_for('index'))
        flash('User with this nickname already exist')
    return render_template("register.html", form=form,
                           Storage=Storage, Client=Client, Operation=Operation, Ware=Ware, User=User,
                           WareStorage=WareStorage, WareOperation=WareOperation,
                           ROLE_ADMIN=1, ROLE_USER=0)


@app.route('/', methods=['GET', 'POST'])
def index():
    if g.id and g.user is not None and g.user.is_authenticated:
        form = StorageInfoForm()
        if form.validate_on_submit():
            form.create_instance()
            return redirect(url_for('index'))
        return render_template("user_base_page.html", user_id=g.id, c=Client.query.filter_by(user_id=g.id), form=form,
                               Ware=Ware, Storage=Storage, Operation=Operation, Client=Client, User=User,
                               WareStorage=WareStorage, WareOperation=WareOperation,
                               ROLE_ADMIN=1, ROLE_USER=0)
    else:
        flash("You must be logged in to access index page")
        return redirect(url_for('login'))


@login_required
@app.route('/new_operation', methods=['GET', 'POST'])
def new_operation():
    form = NewOperationForm()
    if form.validate_on_submit():
        form.create_instance(g.id)
        flash("Added new request")
        return redirect(url_for("index"))
    return render_template("new_operation.html", form=form, user_id=g.id,
                           Ware=Ware, Storage=Storage, Operation=Operation, Client=Client, User=User,
                           WareStorage=WareStorage, WareOperation=WareOperation,
                           ROLE_ADMIN=1, ROLE_USER=0)


@login_required
@app.route('/handle_request', methods=['GET', 'POST'])
def handle_request():
    form = HandleRequestForm()
    _requests = sorted(Operation.query.filter_by(handled=0), key=lambda _: _.date_time)
    if len(_requests) != 0:
        _requests_in = list(filter(lambda _: _.operation_type == "завоз" or _.operation_type == "Завоз"
                                         or _.operation_type == "ЗАВОЗ", _requests))
        _request = _requests_in[0] if len(_requests_in) != 0 else _requests[0]
        if _request:
            if _request.operation_type == "завоз" or _request.operation_type == "Завоз" \
                    or _request.operation_type == "ЗАВОЗ":
                if form.validate_on_submit():
                    handle_in(_request, form)
                    return after_handle(_request)
                return render_template("handle_request.html", form=form, ad_form=HandleRequestForm(),
                                       request=_request, user_id=g.id,
                                       Ware=Ware, Storage=Storage, Operation=Operation, Client=Client, User=User,
                                       WareStorage=WareStorage, WareOperation=WareOperation,
                                       ROLE_ADMIN=1, ROLE_USER=0)
            elif _request.operation_type == "вывоз" or _request.operation_type == "Вывоз" \
                    or _request.operation_type == "ВЫВОЗ":
                for string in handle_out(_request):
                    flash(string)
                after_handle(_request)
    flash("No requests allowed")
    return redirect(url_for('storage_ware'))


def after_handle(_request):
    flash("HANDLED REQUEST {} {}".format(_request.operation_type.upper(),
                                         _request.date_time.strftime('%d/%m/%Y')))
    return redirect(url_for("storage_ware"))


def handle_in(_request, form):
    for i in range(len(form.inputs)):
        s = Storage.query.get(int(form.inputs.data[i]))
        stw = WareStorage.query.filter_by(storage_id=s.id, ware_id=_request.op_ware[i].ware_id).first()
        if not stw:
            stw = WareStorage(ware_id=_request.op_ware[i].ware_id,
                              ware_count=_request.op_ware[i].ware_count,
                              storage_id=s.id)
        else:
            stw.ware_count += _request.op_ware[i].ware_count
        s.st_ware.append(stw)
        db.session.add(s)
        db.session.add(stw)
    _request.handled = 1
    db.session.add(_request)
    db.session.commit()


def handle_out(_request):
    outp = []
    for op_w in _request.op_ware:
        w_count = op_w.ware_count
        for s in Storage.query.all():
            if  w_count != 0:
                sopw = list(filter(lambda _: _.ware_id == op_w.ware_id, s.st_ware))[0]
                if sopw:
                    _min = min(sopw.ware_count, op_w.ware_count)
                    sopw.ware_count -= _min
                    w_count -= _min
            else:
                break
        if op_w.ware_count > 0:
            outp.append("We are missing {} of {}".format(op_w.ware_count, Ware.query.get(op_w.ware_id).name))
        elif op_w.ware_count == 0:
            outp.append("We are ok with {}".format(Ware.query.get(op_w.ware_id).name))
    _request.handled = 1
    db.session.add(_request)
    db.session.commit()
    return outp


@app.route('/storage_info/<_id>', methods=['GET', 'POST'])
def storage_info(_id):
    form = StorageInfoForm()
    if form.validate_on_submit():
        form.create_instance(_id)
        return redirect(url_for('storage_info', _id=0))
    return render_template("storage_info.html", form=form, user_id=g.id, st_id=int(_id),
                           Ware=Ware, Storage=Storage, Operation=Operation, Client=Client, User=User,
                           WareStorage=WareStorage, WareOperation=WareOperation,
                           ROLE_ADMIN=1, ROLE_USER=0)


@app.route('/storage_ware', methods=['GET', 'POST'])
def storage_ware():
    ad_form = HandleRequestForm()
    if ad_form.validate_on_submit():
        i = 0
        for s in Storage.query.all():
            for stw in s.st_ware:
                stw.ware_count = ad_form.inputs[i].data
                db.session.add(stw)
                i += 1
        db.session.commit()
        return redirect(url_for('storage_ware'))
    return render_template("storage_ware.html", user_id=g.id, ad_form=ad_form, request=None,
                           Ware=Ware, Storage=Storage, Operation=Operation, Client=Client, User=User,
                           WareStorage=WareStorage, WareOperation=WareOperation,
                           ROLE_ADMIN=1, ROLE_USER=0)


@app.route('/client_info', methods=['GET', 'POST'])
def client_info():
    return render_template("client_info.html", user_id=g.id,
                           Ware=Ware, Storage=Storage, Operation=Operation, Client=Client, User=User,
                           WareStorage=WareStorage, WareOperation=WareOperation,
                           ROLE_ADMIN=1, ROLE_USER=0)


@app.route('/delete_user/<user_id>')
def delete_user(_user_id):
    if g.user.role == ROLE_ADMIN:
        db.session.delete(User.query.get(_user_id))
        db.session.delete(Client.query.filter_by(user_id=_user_id).first())
        db.session.commit()
    else:
        flash('Нет, соре')
        return redirect(url_for('client_info') or url_for('index'))
    return redirect(url_for('client_info'))


def Clear_DB():
    for t in [Client, Storage, Operation, Ware, WareOperation, WareStorage, User]:
        for t1 in t.query.all():
            db.session.delete(t1)
    db.session.commit()


def Print_DB():
    for t in [Client, Storage, Operation, Ware, WareOperation, WareStorage, User]:
        yield t.query.all()


if __name__ == '__main__':
    print(User.query.all())
    print(Client.query.all())
    app.run(debug=True)
