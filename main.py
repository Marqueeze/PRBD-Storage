from flask import render_template, flash, redirect, url_for, request, g
from models import *
from __init__ import app, db


@app.route('/', methods=['GET', 'POST'])
def index():
    c = Client(name='Ochen sex')
    db.session.add(c)
    db.session.commit()
    return 'Test'


def Clear_DB():
    for t in [Client, Storage, Operation, Ware]:
        for t1 in t.query.all():
            db.session.delete(t1)
    db.session.commit()


def Print_DB():
    for t in [Client, Storage, Operation, Ware]:
        print(t.query.all())


if __name__ == '__main__':
    #Clear_DB()
    Print_DB()
    app.run(debug = True)
