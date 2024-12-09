from flask import render_template, url_for, flash, redirect, request
from flaskapp import app, db, bcrypt
from flaskapp.forms import RegistrationForm, LoginForm
from flaskapp.models import User, ServiceProvider, ServiceOrder, Service, ServiceProviderService, CategoryEnum
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    services_data = getservices()  # Fetch services grouped by categories
    servicesList = []

    # Flatten the data structure to pass as a list of services
    for category, service in services_data.items():
        service["category"] = category  # Add category information to each service
        servicesList.append(service)

    return render_template('home.html', services = servicesList)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


def getservices():
    categories = db.session.query(Service.category).distinct().all()
    obj = {}
    for cat in categories:
        category = cat[0]  # Extract the Enum value from the tuple
        # Fetch the top-rated service for the current category
        top_service = (
            db.session.query(Service).filter(Service.category == category).order_by(Service.ratings.desc()).first()
        )
        if top_service:
            obj[category.value] = { 
                "id": top_service.id,
                "title": top_service.title,
                "description": top_service.description,
                "price": top_service.ser_price,
                "ratings": top_service.ratings,
                "duration": top_service.duration,
            }
    return obj
    
    



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





# @app.route('/addser')
# def addser():
    