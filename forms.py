from flask_wtf import Form
from wtforms import StringField, TextAreaField, IntegerField, PasswordField, FieldList, SelectField
from wtforms.validators import Regexp, NoneOf, URL, Optional, DataRequired, EqualTo, Length, Email
from models import *
from config import ROLE_USER, ROLE_ADMIN, ADMIN_PASSWORD


class EntityForm(Form):
    def get_item(self, i):
        return {
            0: self.id,
        }[i]

    def finder(self, contents: list):
        for i in range(len(self)):
            if self.get_item(i).data:
                # contents = list(filter(lambda x: x.get_item(i) == self.get_item(i).data, contents))
                contents = list(filter(lambda x: str(self.get_item(i).data) in str(x.get_item(i)), contents))
        return contents

    def __len__(self):
        return 3

    # def __iter__(self):
    #     for i in range(len(self)):
    #         yield self.get_item(i)


class StorageInfoForm(EntityForm):
    phone_number = StringField('phone_number', validators=[Regexp('(\+7\d{10})|(8\d{10})',
                                                                  message="Phone number should be +7XXXXXXXXXX or "
                                                                          "8XXXXXXXXXXX format"), DataRequired()])
    address = StringField('address', validators=[Regexp('(.|\n)+'), DataRequired()])

    def get_item(self, index):
        return {
            0: self.phone_number,
            1: self.address,
        }[index]

    def __len__(self):
        return 2

    def create_instance(self, _id=0):
        if _id == 0:
            s = Storage()
        else:
            s = Storage.query.get(_id)
        s.phone_number = self.phone_number.data
        s.address = self.address.data.lower()
        db.session.add(s)
        db.session.commit()


class ClientInfoForm(EntityForm):
    name = StringField('name', validators=[Regexp('(.|\n)+'), DataRequired()])

    def __len__(self):
        return 1

    def get_item(self, index):
        return {
            0: self.name
        }[index]

    def create_instance(self, _id=0):
        if _id == 0:
            c = Client()
        else:
            c = Client.query.get(_id)
        c.name = self.name.data.lower()
        db.session.add(c)
        db.session.commit()


class LoginForm(Form):
    login = StringField('login', validators = [DataRequired()])
    password = PasswordField('password', validators = [DataRequired()])


class RegisterForm(Form):
    login = StringField('login', validators=[DataRequired(), Length(min=4)])
    name = StringField('name', validators=[DataRequired(), Length(min=6)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8)])
    double_password = PasswordField('double_password', validators=[
        DataRequired(),
        EqualTo('password', "Passwords are different"),
        Length(min=8)
    ]
    )
    special_password = PasswordField('special_password')

    # def create_instance(self, _id=0):
    #     u = User(login=self.login.data.lower(), password=self.password.data.lower())
    #     if self.special_password == ADMIN_PASSWORD:
    #         u.role = ROLE_ADMIN
    #     if u.role == ROLE_USER:
    #         c = Client(name=self.name.data.lower())
    #         db.session.add(c)
    #     db.session.add(u)
    #     db.session.commit()


class NewOperationForm(EntityForm):
    operation_type = SelectField('operation_type', choices=[("завоз", "Завоз"), ("вывоз", "Вывоз")],
                                 validators=[DataRequired()])
    wares = StringField('wares', validators=[Regexp('([\w\s]+:\d+,?\s*)+')])

    def create_instance(self, _id=0):
        c = Client.query.filter_by(user_id=_id).first()
        date_time = datetime.today()
        o = Operation(operation_type=self.operation_type.data.lower(), client_id=c.id, date_time=date_time)
        c.operations.append(o)
        db.session.add(o)
        db.session.add(c)
        db.session.commit()
        added_wop = [self.operation_type.data.lower()]
        for pare in self.wares.data.lower().replace(',', ' ').split(' '):
            if pare:
                splitted_pare = pare.split(':')
                w = Ware.query.filter_by(name=splitted_pare[0].lower()).first()
                if not w:
                    w = Ware(name=splitted_pare[0].lower())
                    db.session.add(w)
                    db.session.commit()
                ware_op = WareOperation(ware_id=w.id,
                                        ware_count=int(splitted_pare[1]),
                                        operation_id=o.id)
                added_wop.append({ware_op.ware_id: ware_op.ware_count})
                o.op_ware.append(ware_op)
                w.op_ware.append(ware_op)
                db.session.add(ware_op)
                db.session.add(w)
        db.session.add(o)
        db.session.commit()
        return added_wop


class HandleRequestForm(Form):
    inputs = FieldList(StringField(validators=[DataRequired()]))

