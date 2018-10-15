from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('login', String(length=256)),
    Column('password', String(length=128)),
    Column('role', Integer, default=ColumnDefault(0)),
)

ware = Table('ware', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('name', VARCHAR(length=512)),
    Column('price', FLOAT),
)

operation = Table('operation', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('id_Client', INTEGER),
    Column('operation_type', VARCHAR(length=16)),
    Column('date_time', TIMESTAMP),
)

operation = Table('operation', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('client_id', Integer),
    Column('operation_type', String(length=16)),
    Column('date_time', TIMESTAMP),
)

client = Table('client', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=256)),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].create()
    pre_meta.tables['ware'].columns['price'].drop()
    pre_meta.tables['operation'].columns['id_Client'].drop()
    post_meta.tables['operation'].columns['client_id'].create()
    post_meta.tables['client'].columns['user_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].drop()
    pre_meta.tables['ware'].columns['price'].create()
    pre_meta.tables['operation'].columns['id_Client'].create()
    post_meta.tables['operation'].columns['client_id'].drop()
    post_meta.tables['client'].columns['user_id'].drop()
