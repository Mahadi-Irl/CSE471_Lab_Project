from flask import render_template, url_for, flash, redirect, request
from flaskapp import app, db, bcrypt
from flaskapp.forms import RegistrationForm, LoginForm
from flaskapp.models import User, ServiceProvider, ServiceOrder, Service, ServiceProviderService
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from flaskapp.forms import AddServiceForm

services = [
    {
        'title' : 'Cleaning House',
        'service_provider' : 'Shakib',
        'description' : 'Deep cleaning of the whole house',
        'date_posted' : 'April 25, 2024'
    },
    {
        'title' : 'Washing Toilet',
        'service_provider' : 'Tamim',
        'description' : 'Deep cleaning of the toilet',
        'date_posted' : 'May 12, 2024'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', services=services)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')


@app.route('/dashboard')
@login_required
def dashboard():
    service_requests = ServiceOrder.query.filter_by(customer_id=current_user.id, status="Pending").all()
    current_bookings = ServiceOrder.query.filter_by(customer_id=current_user.id, status="Scheduled").all()
    booking_history = ServiceOrder.query.filter_by(customer_id=current_user.id, status="Completed").all()

    return render_template('dashboard.html', service_requests=service_requests, current_bookings=current_bookings, booking_history=booking_history)


@app.route('/add_service', methods=['GET', 'POST'])
@login_required
def add_service():
    form = AddServiceForm()
    if form.validate_on_submit():
        new_service = ServiceOrder(
            customer_id=current_user.id,
            service_id=None,  # Update if there's a Service model
            title=form.title.data,
            description=form.description.data,
            date_requested=form.date_requested.data,
            status="Pending"
        )
        print(new_service)
        db.session.add(new_service)
        db.session.commit()
        flash('Service added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_service.html', form=form)



@app.route('/service_requests')
def service_requests():
    service_requests = ServiceOrder.query.filter_by(customer_id=current_user.id, status="Pending").all()
    return render_template('service_requests.html', service_requests=service_requests)

@app.route('/current_bookings')
def current_bookings():
    current_bookings = ServiceOrder.query.filter_by(customer_id=current_user.id, status="Scheduled").all()
    return render_template('current_bookings.html', current_bookings=current_bookings)

@app.route('/booking_history')
def booking_history():
    booking_history = ServiceOrder.query.filter_by(customer_id=current_user.id, status="Completed").all()
    return render_template('booking_history.html', booking_history=booking_history)

