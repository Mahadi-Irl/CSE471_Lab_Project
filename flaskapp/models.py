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
    orders = db.relationship('Order', backref='customer', lazy=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    services = db.relationship('Service', backref='creator', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class ServiceProvider(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    nid = db.Column(db.String(50), unique=True, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    services = db.relationship('Service', backref='provider', lazy=True)
    latitude = db.Column(db.Float)  
    longitude = db.Column(db.Float)

    def __repr__(self):
        return f"ServiceProvider('{self.nid}', '{self.bio}')"


class ServiceProviderService(db.Model):
    __tablename__ = 'service_provider_service'
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), primary_key=True)
    service_provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), primary_key=True)





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


    orders = db.relationship('Order', backref='linked_service', lazy=True) 
    
    def __repr__(self):
        return f'<Service {self.id},Title: {self.title}, Category: {self.category.value}, Date: {self.date_posted}>'
    
    def set_ratings(self, value):
        if 0 <= value <= 5:
            self.ratings = value
        else:
            raise ValueError("Ratings must be between 0 and 5") 



class OrderStatus(Enum):
    pending = 'pending'
    accepted = 'accepted'
    on_the_way = 'on the way'
    reached = 'reached'
    completed = 'completed'
    rejected = 'rejected'


class NotificationStatus(Enum):
    not_viewed = 'not viewed'
    viewed = 'viewed'
    

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
    latitude = db.Column(db.Float)  # Add this field
    longitude = db.Column(db.Float)
    
    #review = db.Column(db.String(500), nullable=True)  
    #rate = db.Column(db.Float, nullable=True)  
    rate = db.Column(db.Integer, nullable=True)  # Add this line
    review = db.Column(db.Text, nullable=True)  # Add this line

    service = db.relationship('Service', backref='linked_orders', lazy=True)
    def __repr__(self):
        return f'<Order {self.id}, Location: {self.order_loc}, Price: {self.price}, Status: {self.status.value}, Notifications: {self.notifications.value}>'



class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    resolved = db.Column(db.Boolean, nullable=False, default=False)
    action_taken = db.Column(db.String(100), nullable=True)

    order = db.relationship('Order', backref='complaints', lazy=True)
    user = db.relationship('User', backref='complaints', lazy=True)

    def __repr__(self):
        return f"Complaint('{self.id}', '{self.date_posted}', '{self.message}')"