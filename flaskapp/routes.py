import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flaskapp import app, db, bcrypt
from flaskapp.models import User, ServiceProvider, ServiceOrder, Service, ServiceProviderService, CategoryEnum
from flaskapp.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flask_login import login_user, current_user, logout_user, login_required
from enum import Enum
from sqlalchemy import or_


@app.route("/")
@app.route("/home")
def home():
    services_data = getservices()  
    servicesList = []

    
    for category, service in services_data.items():
        service["category"] = category  
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


@app.route('/servicedetails/<int:service_id>')
def servicedetails(service_id):
    services = Service.query.filter_by(id=service_id).first()
    return render_template('service_details.html', details=services)
    
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
        duration = request.form.get('duration') 
        
        
        if not nid or not bio or not title or not description or not ser_price or not category:
            flash('All fields are required.', 'danger')
            return redirect(url_for('become_service_provider'))
        
        # Create and save the service provider
        
        service_provider =  db.session.query(ServiceProvider).filter(ServiceProvider.id == current_user.id).first()
        
        if ( service_provider == None):
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
            category=category,  # Store the selected category
            duration = duration,
        )
        db.session.add(service)
        db.session.commit()

        flash('You are now a service provider!', 'success')
        return redirect(url_for('home')) 


#search
@app.route('/search_result', methods=['GET'])
def search_result():
    query = request.args.get('query', '').split()
    min_price = request.args.get('min_price', type=float)  
    max_price = request.args.get('max_price', type=float)  
    rating = request.args.get('rating', type=int) or 0   
    
    results = Service.query 
    
    if query:
        filters = [Service.title.ilike(f"%{word}%") for word in query]
        results = results.filter(or_(*filters))

    if min_price is not None:
        results = results.filter(Service.ser_price >= min_price)

    if max_price is not None:
        results = results.filter(Service.ser_price <= max_price)

    if rating >= 0 and rating <=5:
        results = results.filter(Service.ratings >= rating)

    # Apply sorting after all filters
    results = results.order_by(Service.ser_price.asc(), Service.ratings.desc()).all()

    return render_template('search_results.html', result=results)
        


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/alluserorders')
@login_required
def alluserorders():
    orders = ServiceOrder.query.filter_by(customer_id=current_user.id).all()
    return render_template('alluserorders.html', orders=orders)




@app.route('/userorderdetails/<int:order_id>')
@login_required
def userorderdetails(order_id):
    # Fetch the specific order belonging to the logged-in user
    order = ServiceOrder.query.filter_by(id=order_id, customer_id=current_user.id).first()

    if not order:
        flash('Order not found', 'danger')
        return redirect(url_for('alluserorders'))

    return render_template('userorderdetails.html', details=order)




@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)



