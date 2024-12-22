from datetime import datetime
from flaskapp import db, login_manager, app
from flask_login import UserMixin
from enum import Enum
from sqlalchemy.orm import validates


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    orders = db.relationship('ServiceOrder', backref='customer', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class ServiceProvider(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    nid = db.Column(db.String(50), unique=True, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    services = db.relationship('Service', backref='provider', lazy=True)

    def __repr__(self):
        return f"ServiceProvider('{self.nid}', '{self.bio}')"


class ServiceProviderService(db.Model):
    __tablename__ = 'service_provider_service'
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), primary_key=True)
    service_provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), primary_key=True)


class ServiceOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    service_provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), nullable=False)
    service = db.relationship('Service', backref='orders', lazy=True)

    def __repr__(self):
        return f"ServiceOrder('Order #{self.id}', 'Customer: {self.customer.username}', 'Service: {self.service.title}', 'Provider: {self.service_provider.name}', 'Status: {self.status}')"


class CategoryEnum(Enum):
    ELECTRONICS = 'AC Servicing'
    FASHION = 'Salon Care'
    HOME = 'Home Cleaning'
    BOOKS = 'Stationary Services'
    SPORTS = 'Practice Matches'


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), nullable=False)  
    ratings = db.Column(db.Integer, nullable=False)
    category = db.Column(db.Enum(CategoryEnum), nullable=False)
    duration = db.Column(db.Integer, nullable = False)
    ser_price = db.Column(db.Float, nullable=False) 
    
    def __repr__(self):
        return f"Post('{self.title}', '{self.category}',  '{self.date_posted}')"
    
    def set_ratings(self, value):
        if 0 <= value <= 5:
            self.ratings = value
        else:
            raise ValueError("Ratings must be between 0 and 5") # must see if this works


class OrderStatus(Enum):
    pending = 'pending'
    accepted = 'accepted'
    on_the_way = 'on the way'
    reached = 'reached'
    completed = 'completed'


class NotificationStatus(Enum):
    not_viewed = 'not viewed'
    viewed = 'viewed'
    rejected = 'rejected'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_loc = db.Column(db.String(200), nullable=False)  
    order_datetime = db.Column(db.DateTime, default=datetime.utcnow)  
    status = db.Column(db.Enum(OrderStatus), nullable=False, default=OrderStatus.pending)  
    review = db.Column(db.String(500), nullable=True)  
    rate = db.Column(db.Float, nullable=True)  
    price = db.Column(db.Float, nullable=False) 
    notifications = db.Column(db.Enum(NotificationStatus), default=NotificationStatus.not_viewed) 
    ser_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), nullable=False)
    

    def __repr__(self):
        return f'<Order {self.id}, Location: {self.order_loc}, Price: {self.price}, Status: {self.status}, Notifications: {self.notifications}>'
