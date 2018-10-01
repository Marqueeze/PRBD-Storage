from flask import render_template, flash, redirect, url_for, request, g
from models import *
from __init__ import app, db


@app.route('/', methods=['GET', 'POST'])
def index():
    return str(Print_DB())


@app.route('/Client', methods=['GET', 'POST'])
def client():
    # c = Client(name='Дмитрий Иванович Соломатин')
    w = Ware(name="Классы", price=0.01)
    # o = Operation(id_Client=1, operation_type='+')
    # op_w = WareOperation(ware_count=15)
    # op_w.wares = w
    # o.op_ware.append(op_w)
    # db.session.add(c)
    # db.session.add(w)
    # db.session.add(o)
    st_w = WareStorage(ware_count=15)
    st_w.wares = w
    s = Storage.query.get(1)
    s.st_ware.append(st_w)
    db.session.add(s)
    db.session.commit()
    return 'Client added'


@app.route('/Ware', methods=['GET', 'POST'])
def ware():
    c = Ware(name="Классы", price=0.01)
    db.session.add(c)
    db.session.commit()
    return 'Ware added'


@app.route('/Storage', methods=['GET', 'POST'])
def storage():
    c = Storage(phone_number='88005553535', address='Улица Пушкина Дом Колотушкина')
    # c.wares.append(Ware.query.filter_by(name='Классы').first())
    db.session.add(c)
    db.session.commit()
    return "Storage added"


@app.route('/Operation', methods=['GET', 'POST'])
def operation():
    c = Operation(id_Client = 1, operation_type = '+')
    op_w = WareOperation(ware_count=15)
    op_w.wares = Ware.query.filter_by(name="Классы").first()
    c.wares.append(op_w)
    db.session.commit()
    return 'Operation added'


def Clear_DB():
    for t in [Client, Storage, Operation, Ware, WareOperation]:
        for t1 in t.query.all():
            db.session.delete(t1)
    db.session.commit()


def Print_DB():
    for t in [Client, Storage, Operation, Ware, WareOperation]:
        yield t.query.all()

if __name__ == '__main__':
    #Clear_DB()
    for x in list(Print_DB()):
        print(x)
    app.run(debug = True)
