from __init__ import db
from datetime import datetime
from config import ROLE_ADMIN, ROLE_USER


class WareOperation(db.Model):
    ware_id = db.Column(db.Integer, db.ForeignKey('ware.id', onupdate='CASCADE'), primary_key=True)
    operation_id = db.Column(db.Integer, db.ForeignKey('operation.id', onupdate='CASCADE'), primary_key=True)
    ware_count = db.Column(db.INTEGER, default=1)
    wares = db.relationship("Ware", back_populates='op_ware')
    operations = db.relationship("Operation", back_populates='op_ware')

    def __repr__(self):
        return "Ware_id: {}, Ware_count: {}".format(self.ware_id, self.ware_count)


class WareStorage(db.Model):
    ware_id = db.Column(db.Integer, db.ForeignKey('ware.id', onupdate='CASCADE'), primary_key=True)
    storage_id = db.Column(db.Integer, db.ForeignKey('storage.id', onupdate='CASCADE'), primary_key=True)
    ware_count = db.Column(db.INTEGER, default=1)
    wares = db.relationship("Ware", back_populates='st_ware')
    storages = db.relationship("Storage", back_populates='st_ware')

    def __repr__(self):
        return "Ware_id: {}, Storage_id: {}, Ware_count: {}".format(self.ware_id, self.storage_id, self.ware_count)


class Storage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(16), index=True, unique=True)
    address = db.Column(db.String(256), index=True, unique=True)

    st_ware = db.relationship("WareStorage", cascade='all')

    def __repr__(self):
        return "Storage {}".format(self.address)


class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    operation_type = db.Column(db.String(16), index=True)
    date_time = db.Column(db.TIMESTAMP)
    handled = db.Column(db.Integer, default=0, index=True)

    op_ware = db.relationship("WareOperation", back_populates='operations', cascade='all')

    def __repr__(self):
        return "Operation {}".format(self.operation_type)


class Ware(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), index=True)

    st_ware = db.relationship("WareStorage", back_populates="wares", cascade='all')
    op_ware = db.relationship("WareOperation", back_populates='wares', cascade='all')

    def __repr__(self):
        return "Ware {}".format(self.name)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    operations = db.relationship('Operation')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return "Client {}".format(self.name)

    def get_item(self, index):
        return {
            0: self.name,
            1: self.operations
        }[index]


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(256), index=True)
    password = db.Column(db.String(128))
    role = db.Column(db.Integer, default=ROLE_USER)

    def __repr__(self):
        return "Id: {}, Role: {}".format(self.id, self.role)
