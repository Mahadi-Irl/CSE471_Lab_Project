from datetime import datetime
from flaskapp import db, login_manager
from flask_login import UserMixin
from enum import Enum

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

    @property
    def is_service_provider(self):
        return ServiceProvider.query.filter_by(id=self.id).first() is not None

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class ServiceProvider(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    nid = db.Column(db.String(50), unique=True, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    services = db.relationship('Service', backref='provider', lazy=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    verified = db.Column(db.Boolean, nullable=False, default=False)
    user = db.relationship('User', backref='service_provider', lazy=True)

    def __repr__(self):
        return f"ServiceProvider('{self.nid}', '{self.bio}', Verified: {self.verified})"

class ServiceProviderService(db.Model):
    __tablename__ = 'service_provider_service'
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), primary_key=True)
    service_provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), primary_key=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    services = db.relationship('Service', backref='category', lazy=True)

    def __repr__(self):
        return f"Category('{self.name}')"

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), nullable=False)
    ratings = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    ser_price = db.Column(db.Float, nullable=False)
    orders = db.relationship('Order', backref='linked_service', lazy=True)

    def __repr__(self):
        return f'<Service {self.id}, Title: {self.title}, Category: {self.category.name}, Date: {self.date_posted}>'

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
    review = db.Column(db.Text, nullable=True)
    rate = db.Column(db.Integer, nullable=True)
    price = db.Column(db.Float, nullable=False)
    notifications = db.Column(db.Enum(NotificationStatus), default=NotificationStatus.not_viewed)
    ser_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    service = db.relationship('Service', backref='service_orders', lazy=True)  # Renamed backref
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

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

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications', lazy=True)

    def __repr__(self):
        return f"Notification('{self.id}', '{self.message}', '{self.date_posted}')"

def create_dummy_data():
    from flaskapp import db
    from flaskapp.models import User, ServiceProvider, Service, Order, Category, Complaint, Notification
    from datetime import datetime

    # Create dummy users
    user1 = User(username='user1', email='user1@example.com', password='password', is_admin=False)
    user2 = User(username='user2', email='user2@example.com', password='password', is_admin=False)
    user3 = User(username='user3', email='user3@example.com', password='password', is_admin=False)
    user4 = User(username='user4', email='user4@example.com', password='password', is_admin=False)
    admin = User(username='admin', email='admin@example.com', password='password', is_admin=True)
    db.session.add_all([user1, user2, user3, user4, admin])
    db.session.commit()

    # Create dummy service providers
    sp1 = ServiceProvider(id=user1.id, nid='123456789', bio='Service Provider 1 Bio', verified=True, latitude=23.8103, longitude=90.4125)  # Dhaka
    sp2 = ServiceProvider(id=user2.id, nid='987654321', bio='Service Provider 2 Bio', verified=False, latitude=22.3475, longitude=91.8123)  # Chittagong
    sp3 = ServiceProvider(id=user3.id, nid='112233445', bio='Service Provider 3 Bio', verified=True, latitude=24.3636, longitude=88.6241)  # Rajshahi
    db.session.add_all([sp1, sp2, sp3])
    db.session.commit()

    # Create dummy categories
    cat1 = Category(name='Cleaning')
    cat2 = Category(name='Plumbing')
    cat3 = Category(name='Electrical')
    db.session.add_all([cat1, cat2, cat3])
    db.session.commit()

    # Create dummy services
    service1 = Service(title='House Cleaning', description='Full house cleaning service', user_id=user1.id, provider_id=sp1.id, ratings=4, category_id=cat1.id, duration=2, ser_price=50.0)
    service2 = Service(title='Pipe Fixing', description='Fixing all kinds of pipes', user_id=user2.id, provider_id=sp2.id, ratings=5, category_id=cat2.id, duration=1, ser_price=30.0)
    service3 = Service(title='Electrical Repair', description='Repairing electrical issues', user_id=user3.id, provider_id=sp3.id, ratings=3, category_id=cat3.id, duration=3, ser_price=70.0)
    db.session.add_all([service1, service2, service3])
    db.session.commit()

    # Create dummy orders
    order1 = Order(order_loc='123 Main St', order_datetime=datetime.utcnow(), status='pending', price=50.0, ser_id=service1.id, service_provider_id=sp1.id, customer_id=user2.id, latitude=23.8103, longitude=90.4125)  # Dhaka
    order2 = Order(order_loc='456 Elm St', order_datetime=datetime.utcnow(), status='completed', price=30.0, ser_id=service2.id, service_provider_id=sp2.id, customer_id=user1.id, latitude=22.3475, longitude=91.8123)  # Chittagong
    order3 = Order(order_loc='789 Oak St', order_datetime=datetime.utcnow(), status='accepted', price=70.0, ser_id=service3.id, service_provider_id=sp3.id, customer_id=user4.id, latitude=24.3636, longitude=88.6241)  # Rajshahi
    db.session.add_all([order1, order2, order3])
    db.session.commit()

    # Create dummy complaints
    complaint1 = Complaint(order_id=order1.id, user_id=user2.id, message='Service was not satisfactory', date_posted=datetime.utcnow(), resolved=False)
    complaint2 = Complaint(order_id=order3.id, user_id=user4.id, message='Service was delayed', date_posted=datetime.utcnow(), resolved=False)
    db.session.add_all([complaint1, complaint2])
    db.session.commit()

    # Create dummy notifications
    notification1 = Notification(user_id=user1.id, message='Your complaint has been received', date_posted=datetime.utcnow())
    notification2 = Notification(user_id=user4.id, message='Your order has been accepted', date_posted=datetime.utcnow())
    db.session.add_all([notification1, notification2])
    db.session.commit()

    print("Dummy data created successfully!")