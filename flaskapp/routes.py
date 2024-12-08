from flask import render_template, url_for, flash, redirect, request
from flaskapp import app, db, bcrypt
from flaskapp.forms import RegistrationForm, LoginForm
from flaskapp.models import User, ServiceProvider, ServiceOrder, Service, ServiceProviderService, CategoryEnum
from flask_login import login_user, current_user, logout_user, login_required
from enum import Enum


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


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

@app.route('/join')
def join():
    return redirect(url_for('containform'))

@app.route("/containform")
def containform():
    return render_template("createServiceProviderprofileform.html")

@app.route('/become_service_provider', methods=['GET', 'POST'])
@login_required
def become_service_provider():
    if request.method == 'POST':
        nid = request.form.get('nid')
        bio = request.form.get('bio')
        title = request.form.get('title')
        description = request.form.get('description')
        ser_price = request.form.get('ser_price')
        category = request.form.get('category')  
        
        
        if not nid or not bio or not title or not description or not ser_price or not category:
            flash('All fields are required.', 'danger')
            return redirect(url_for('become_service_provider'))
        
        # Create and save the service provider
        service_provider = ServiceProvider(id=current_user.id, nid=nid, bio=bio)
        db.session.add(service_provider)
        db.session.commit()

        # Create and save the service with the selected category
        service = Service(
            title=title, 
            description=description, 
            ser_price=ser_price, 
            user_id=current_user.id, 
            provider_id=current_user.id,
            ratings = 1,
            category=category  # Store the selected category
        )
        db.session.add(service)
        db.session.commit()

        flash('You are now a service provider!', 'success')
        return redirect(url_for('home')) 





    


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')





# @app.route('/addser')
# def addser():
    