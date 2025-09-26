from datetime import datetime, timezone
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

 
# --------------------------
# User Model
# --------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='client')  
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    services = db.relationship('Service', backref='provider', lazy=True)
    bookings = db.relationship('Booking', backref='client', lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)

# Service, Booking, Payment models (unchanged)...
# --------------------------
# Service Model
# --------------------------
class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200))  # for geo-location matching
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bookings = db.relationship('Booking', backref='service', lazy=True)

    def __repr__(self):
        return f"<Service {self.title}>"


# --------------------------
# Booking Model
# --------------------------
class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default="pending")  
    scheduled_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    payment = db.relationship('Payment', uselist=False, backref='booking')

    def __repr__(self):
        return f"<Booking {self.id} - {self.status}>"


# --------------------------
# Payment Model
# --------------------------
class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(50), default="mpesa")  
    status = db.Column(db.String(20), default="pending")
    transaction_id = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)

    def __repr__(self):
        return f"<Payment {self.id} - {self.status}>"

