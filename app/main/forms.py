from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,RadioField,SelectField,SubmitField,TextAreaField
from wtforms.validators import Required, Email,EqualTo
from ..models import User,Ticket,Role
from wtforms import ValidationError
import wtforms_sqlalchemy.fields as f
from wtforms_sqlalchemy.fields import QuerySelectField


def get_pk_from_identity(obj):
   cls, key = f.identity_key(instance=obj)[:2]
   return ':'.join(f.text_type(x) for x in key)
f.get_pk_from_identity = get_pk_from_identity

def user_query():
   users = User.query.filter_by(role_id = 2).all()
   return users

def role_query():
   return Role.query

class TicketForm(FlaskForm):
    subject = StringField('Ticket Subject',validators=[Required()])
    description = TextAreaField('Ticket Description', validators=[Required()])
    severity = RadioField('Severity',validators=[Required()],choices=[('low','Low'),('medium','Medium'),('high','High')])
    technician = QuerySelectField('Choose Technician',query_factory=user_query,allow_blank=True,validators=[Required()])
    submit = SubmitField('Submit Ticket')

class UpdateUserForm(FlaskForm):
    username = StringField('Username',validators=[Required()])
    firstname = StringField('First Name',validators=[Required()])
    lastname = StringField('Last Name', validators=[Required()])
    email = StringField('Email', validators=[Email(), Required()])
    role = QuerySelectField('Role', validators=[Required()],query_factory=role_query,allow_blank=True)
    submit = SubmitField('Update User')

class CreateUserForm(FlaskForm):
    email = StringField('Your Email Address',validators=[Required(),Email()])
    username = StringField('Enter your username',validators = [Required()])
    firstname = StringField('Enter your first name',validators = [Required()])
    lastname = StringField('Enter your last name',validators = [Required()])
    password = PasswordField('Password',validators = [Required(), EqualTo('password_confirm',message = 'Passwords must match')])
    password_confirm = PasswordField('Confirm Passwords',validators = [Required()])
    role = QuerySelectField('Role', validators=[Required()],query_factory=role_query,allow_blank=True)
    submit = SubmitField('Create User')

    def validate_email(self,data_field):
        if User.query.filter_by(email =data_field.data).first():
            raise ValidationError('There is an account with that email')

    def validate_username(self,data_field):
        if User.query.filter_by(username = data_field.data).first():
            raise ValidationError('That username is taken')

class MessageForm(FlaskForm):
    title = StringField('Title',validators=[Required()])
    message = TextAreaField('Message',validators=[Required()])
    submit = SubmitField('Submit Message')
