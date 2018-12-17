from flask import render_template,request,redirect,url_for,abort
from . import main
from ..models import User,Ticket,Role,Message
from .. import db,photos
from .forms import TicketForm, UpdateUserForm, CreateUserForm,MessageForm
from flask_login import login_required,current_user
import datetime
from ..email import mail_message

# Views
@main.route('/')
@login_required
def index():

    '''
    View root page function that returns the index page and its data
    '''

    title = 'Home - Welcome to Perfect Pitch'
    if current_user.role_id == 1:
        return redirect(url_for('.admin'))
    elif current_user.role_id == 2:
        return redirect(url_for('.technician'))
    else:
        return redirect(url_for('.requester'))

    return render_template('index.html',title = title)

@main.route('/admin')
@login_required
def admin():
    open_tickets_list = Ticket.query.filter_by(status = 'open').order_by(Ticket.id.desc()).limit(10)
    progress_tickets_list = Ticket.query.filter_by(status = 'progress').order_by(Ticket.id.desc()).limit(10)
    closed_tickets_list = Ticket.query.filter_by(status = 'closed').order_by(Ticket.id.desc()).limit(10)

    status_labels = ["Open","In progress","Closed"]

    status_values = []

    severity_values = []

    tickets = Ticket.query.all()

    open_count = 0
    progress_count = 0
    closed_count = 0

    high_count = 0
    medium_count = 0
    low_count = 0

    for ticket in tickets:
        if ticket.status == 'open':
            open_count += 1
    status_values.append(open_count)

    for ticket in tickets:
        if ticket.status == 'progress':
            progress_count += 1
    status_values.append(progress_count)

    for ticket in tickets:
        if ticket.status == 'closed':
            closed_count += 1
    status_values.append(closed_count)

    for ticket in tickets:
        if ticket.severity == 'high':
            high_count += 1
    severity_values.append(high_count)

    for ticket in tickets:
        if ticket.severity == 'medium':
            medium_count += 1
    severity_values.append(medium_count)

    for ticket in tickets:
        if ticket.severity == 'low':
            low_count += 1
    severity_values.append(low_count)

    return render_template('admin.html', open_tickets_list = open_tickets_list,progress_tickets_list = progress_tickets_list, closed_tickets_list = closed_tickets_list,status_labels = status_labels, status_values = status_values, severity_values = severity_values)

@main.route('/technician', methods=['GET','POST'])
@login_required
def technician():

    open_tickets_list = Ticket.query.filter_by(status = 'open', assigned_to = current_user.username).order_by(Ticket.id.desc()).limit(10)
    progress_tickets_list = Ticket.query.filter_by(status = 'progress', assigned_to = current_user.username).order_by(Ticket.id.desc()).limit(10)
    closed_tickets_list = Ticket.query.filter_by(status = 'closed', assigned_to = current_user.username).order_by(Ticket.id.desc()).limit(10)
    form = TicketForm()
    if form.validate_on_submit():
        new_ticket = Ticket(ticket_title = form.subject.data,ticket_description = form.description.data, severity = form.severity.data, ticket   = current_user, assigned_to = str(form.technician.data))
        db.session.add(new_ticket)
        db.session.commit()
        user = User.query.filter_by(username = new_ticket.assigned_to).first()
        mail_message('New Ticket Issued','email/new_ticket',user.email,user = user)
        return redirect(url_for('.technician'))
    return render_template('technician.html', form = form, open_tickets_list = open_tickets_list, progress_tickets_list = progress_tickets_list, closed_tickets_list = closed_tickets_list)

@main.route('/requester', methods=['GET','POST'])
@login_required
def requester():

    open_tickets_list = Ticket.query.filter_by(status = 'open', user_id = current_user.id).order_by(Ticket.id.desc()).limit(10)
    progress_tickets_list = Ticket.query.filter_by(status = 'progress', user_id = current_user.id).order_by(Ticket.id.desc()).limit(10)
    closed_tickets_list = Ticket.query.filter_by(status = 'closed', user_id = current_user.id).order_by(Ticket.id.desc()).limit(10)

    form = TicketForm()
    if form.validate_on_submit():
        print(form.technician.data, form.subject.data, form.severity.data)
        new_ticket = Ticket(ticket_title = form.subject.data,ticket_description = form.description.data, severity = form.severity.data, ticket = current_user, assigned_to = str(form.technician.data))
        db.session.add(new_ticket)
        db.session.commit()
        user = User.query.filter_by(username = new_ticket.assigned_to).first()
        mail_message('New Ticket Issued','email/new_ticket',user.email,user = user)
        return redirect(url_for('.requester'))
    return render_template('requester.html', form= form, open_tickets_list = open_tickets_list, progress_tickets_list = progress_tickets_list, closed_tickets_list = closed_tickets_list)

@main.route('/users', methods = ['GET','POST'])
def users():
    form = CreateUserForm()

    if form.validate_on_submit():
        role = 0
        if str(form.role.data) == 'admin':
            role = 1
        elif str(form.role.data) == 'technician':
            role = 2
        elif str(form.role.data) == 'requester':
            role = 3
        user = User(email = form.email.data, username = form.username.data,firstname= form.firstname.data,lastname= form.lastname.data,password = form.password.data,role_id = role)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('.users'))

    users = User.query.order_by(User.id.asc()).all()
    return render_template('users.html',users = users, form = form)

@main.route('/admin/tickets')
def admin_tickets():
    tickets = Ticket.query.all()
    return render_template('tickets.html', tickets = tickets)

@main.route('/technician/tickets')
def tech_tickets():
    tech_tickets = Ticket.query.filter_by(assigned_to = current_user.username).all()
    my_tickets = Ticket.query.filter_by(user_id = current_user.id).all()

    return render_template('tech-tickets.html', tech_tickets = tech_tickets, my_tickets = my_tickets)

@main.route('/requester/tickets')
def req_tickets():
    req_tickets = Ticket.query.filter_by(user_id = current_user.id).all()
    return render_template('req-tickets.html', req_tickets = req_tickets)

@main.route('/tickets/ticket/<int:id>', methods = ['GET','POST'])
def ticket(id):
    form = MessageForm()

    ticket = Ticket.query.filter_by(id = id).first()

    if form.validate_on_submit():
        title = form.title.data
        message = form.message.data
        new_message = Message(messages = ticket,message_title = title,message_body = message,message = current_user)
        new_message.save_message()

    messages = Message.get_messages(id)

    print('test')

    return render_template('ticket.html', ticket = ticket, form = form, messages = messages)

@main.route('/user/<int:id>/update', methods = ['GET','POST'])
@login_required
def update_user(id):
    form = UpdateUserForm()
    user = User.query.filter_by(id=id).first()
    if form.validate_on_submit():
        user.username = form.username.data
        user.firstname = form.firstname.data
        user.lastname = form.lastname.data
        user.email = form.email.data
        user.role = form.role.data
        db.session.commit()
        return redirect(url_for('main.users'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.firstname.data = user.firstname
        form.lastname.data = user.lastname
        form.email.data = user.email
        form.role.data = user.role

    return render_template('user.html',form = form)

@main.route('/tickets/ticket/<int:id>/status_progress', methods=['GET','POST'])
def update_progress(id):
    ticket = Ticket.query.filter_by(id = id).first()
    ticket.status = 'progress'
    db.session.commit()
    requester = ticket.ticket
    mail_message('Ticket Status Upgraded!','email/status',requester.email,requester = requester,ticket = ticket)
    return redirect(url_for('main.ticket', id=id))

@main.route('/tickets/ticket/<int:id>/status_closed', methods=['GET','POST'])
def update_closed(id):
    ticket = Ticket.query.filter_by(id = id).first()
    ticket.status = 'closed'
    db.session.commit()
    requester = ticket.ticket
    mail_message('Ticket Status Upgraded!','email/status',requester.email,requester = requester, ticket = ticket)
    return redirect(url_for('main.ticket', id=id))
