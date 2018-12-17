from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from . import login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin,db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(255),index =True)
    firstname = db.Column(db.String(255))
    lastname = db.Column(db.String(255))
    email = db.Column(db.String(255),unique = True,index = True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    bio = db.Column(db.String(5000))
    profile_pic_path = db.Column(db.String)
    pass_secure = db.Column(db.String(255))

    tickets = db.relationship('Ticket',backref = 'ticket',lazy="dynamic")

    messages = db.relationship('Message',backref = 'message',lazy="dynamic")

    @property
    def password(self):
        raise AttributeError('You cannot read the password attribute')

    @password.setter
    def password(self,password):
        self.pass_secure = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.pass_secure,password)

    def __repr__(self):
        return f'{self.username}'

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(255))
    users = db.relationship('User',backref = 'role',lazy="dynamic")

    def __repr__(self):
        return f'{self.name}'

class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer,primary_key = True)
    ticket_title = db.Column(db.String(255))
    ticket_description = db.Column(db.String(255))
    severity = db.Column(db.String(100))
    status = db.Column(db.String(100), default = 'open')
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    assigned_to = db.Column(db.String(255))

    message_id = db.relationship('Message', backref = 'messages',lazy="dynamic")

class Message(db.Model):

    __tablename__ = 'messages'
    all_messages =[]

    id = db.Column(db.Integer,primary_key = True)
    ticket_id = db.Column(db.Integer,db.ForeignKey('tickets.id'))
    message_title = db.Column(db.String)
    message_body = db.Column(db.String)
    posted = db.Column(db.Time,default=datetime.utcnow())
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))


    def save_message(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_messages(cls, id):

        response = []

        for message in Message.query.all():
            if message.ticket_id == id:
                response.append(message)

        return response
