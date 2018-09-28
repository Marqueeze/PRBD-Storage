from __init__ import db
from datetime import datetime

ware_operation = db.Table('ware_operation',
    db.Column('ware_id', db.Integer, db.ForeignKey('ware.id')),
    db.Column('operation_id', db.Integer, db.ForeignKey('operation.id'))
                          )

ware_storage = db.Table('ware_storage',
    db.Column('ware_id', db.Integer, db.ForeignKey('ware.id')),
    db.Column('storage_id', db.Integer, db.ForeignKey('storage.id'))
                          )


class Storage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(16), index=True, unique=True)
    address = db.Column(db.String(256), index=True, unique=True)
    storageble_wares = db.relationship("Ware", secondary=ware_storage, backref="storage")

    def __repr__(self):
        return "Storage id {}".format(self.name)


class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_Client = db.Column(db.Integer, db.ForeignKey('client.id'), index=True)
    ware_count = db.Column(db.INTEGER, default=1)
    operation_type = db.Column(db.String(16), index=True)
    date_time = db.Column(db.TIMESTAMP, default=datetime.now())
    operated_wares = db.relationship("Ware", secondary=ware_operation, backref="operation")

    def __repr__(self):
        return "Operation {}".format(self.name)


class Ware(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), index=True)
    price = db.Column(db.FLOAT, index=True)

    def __repr__(self):
        return "Ware {}".format(self.name)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)

    def __repr__(self):
        return "Client {}".format(self.name)
