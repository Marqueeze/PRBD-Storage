from __init__ import db
from datetime import datetime


class WareOperation(db.Model):
    ware_id = db.Column(db.Integer, db.ForeignKey('ware.id'), primary_key=True)
    operation_id = db.Column(db.Integer, db.ForeignKey('operation.id'), primary_key=True)
    ware_count = db.Column(db.INTEGER, default=1)
    wares = db.relationship("Ware", back_populates='op_ware')
    operations = db.relationship("Operation", back_populates='op_ware')

    def __repr__(self):
        return "Ware_id: {}, Operation_id: {}, Ware_count: {}".format(self.ware_id, self.operation_id, self.ware_count)


class WareStorage(db.Model):
    ware_id = db.Column(db.Integer, db.ForeignKey('ware.id'), primary_key=True)
    storage_id = db.Column(db.Integer, db.ForeignKey('storage.id'), primary_key=True)
    ware_count = db.Column(db.INTEGER, default=1)
    wares = db.relationship("Ware", back_populates='st_ware')
    storages = db.relationship("Storage", back_populates='st_ware')

    def __repr__(self):
        return "Ware_id: {}, Storage_id: {}, Ware_count: {}".format(self.ware_id, self.storage_id, self.ware_count)

# ware_operation = db.Table('ware_operation',
#                           db.Column('ware_id', db.Integer, db.ForeignKey('ware.id')),
#                           db.Column('operation_id', db.Integer, db.ForeignKey('operation.id'))
#                           )


# ware_storage = db.Table('ware_storage',
#                         db.Column('ware_id', db.Integer, db.ForeignKey('ware.id')),
#                         db.Column('storage_id', db.Integer, db.ForeignKey('storage.id'))
#                         )


class Storage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(16), index=True, unique=True)
    address = db.Column(db.String(256), index=True, unique=True)

    st_ware = db.relationship("WareStorage", back_populates="storages")

    def __repr__(self):
        return "Storage {}, St_Ware: {}".format(self.address, self.st_ware)


class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_Client = db.Column(db.Integer, db.ForeignKey('client.id'), index=True)
    client = db.relationship('Client', back_populates='operations')
    operation_type = db.Column(db.String(16), index=True)
    date_time = db.Column(db.TIMESTAMP, default=datetime.now())

    op_ware = db.relationship("WareOperation", back_populates='operations')

    def __repr__(self):
        return "Operation {}, Op_Ware: {}".format(self.operation_type, self.op_ware)


class Ware(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), index=True)
    price = db.Column(db.FLOAT, index=True)

    st_ware = db.relationship("WareStorage", back_populates="wares")
    op_ware = db.relationship("WareOperation", back_populates='wares')

    def __repr__(self):
        return "Ware {}, Op_Ware: {}, St_Ware: {}".format(self.name, self.op_ware, self.st_ware)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    operations = db.relationship('Operation', back_populates='client')

    def __repr__(self):
        return "Client {}, Operations: {}".format(self.name, self.operations)
