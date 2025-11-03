from datetime import datetime, timezone
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, Column, Integer, String, Float, DateTime, ForeignKey, Table

# Association table for many-to-many relationship between User and Role
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    # Relationship
    users = db.relationship('User', secondary=user_roles, back_populates='roles')
    
    def __repr__(self):
        return f'<Role {self.name}>'
 
# --------------------------
# User Model
# --------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    bio = db.Column(db.Text)
    photo = db.Column(db.String(255))  # store image path
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True, default='default_profile.png')
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    professional = db.relationship('Professional', back_populates='user', uselist=False, cascade='all, delete-orphan')
    services = db.relationship('Service', back_populates='provider', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', back_populates='client', lazy=True, cascade='all, delete-orphan')
    reviews_given = db.relationship('Review', back_populates='client', lazy=True, cascade='all, delete-orphan')
    job_postings = db.relationship('Job', back_populates='poster', lazy=True, cascade='all, delete-orphan')
    roles = db.relationship('Role', secondary=user_roles, back_populates='users', lazy='dynamic')
    
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return self.roles.filter(Role.name == role_name).first() is not None

    def __repr__(self):
        return f"<User {self.email}>"

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)
        
    def get_full_name(self):
        """Return the user's full name."""
        if self.first_name:  # This now contains the full name
            return self.first_name
        return self.username or self.email.split('@')[0]
    
    def is_professional(self):
        """Check if the user has a professional profile"""
        return self.professional is not None

# --------------------------
# Professional Model
# --------------------------
class Professional(db.Model):
    __tablename__ = 'professionals'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    profession = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_picture = db.Column(db.String(255), default='default_profile.png')
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    years_experience = db.Column(db.Integer, default=0)
    hourly_rate = db.Column(db.Float, nullable=True)
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)
    location = db.Column(db.String(200))
    skills = db.Column(db.Text, nullable=True)  # Comma-separated skills
    education = db.Column(db.Text, nullable=True)  # Can store JSON or text
    certifications = db.Column(db.Text, nullable=True)  # Can store JSON or text
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)

    # Relationships
    user = db.relationship('User', back_populates='professional')
    services = db.relationship('Service', 
                             back_populates='professional',
                             lazy='dynamic',
                             cascade='all, delete-orphan',
                             foreign_keys='[Service.professional_id]')
    reviews = db.relationship('Review', back_populates='professional', lazy=True, cascade='all, delete-orphan')
    ai_suggestions = db.relationship('AISuggestion', back_populates='professional', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Professional {self.full_name} - {self.profession}>"

    def get_skills_list(self):
        """Return skills as a list"""
        return [skill.strip() for skill in self.skills.split(',')] if self.skills else []

    def add_skill(self, skill):
        """Add a new skill"""
        skills = self.get_skills_list()
        if skill not in skills:
            skills.append(skill)
            self.skills = ', '.join(skills)
            return True
        return False

    def update_rating(self, new_rating):
        """Update professional's rating when a new review is added"""
        if self.rating == 0:
            self.rating = new_rating
        else:
            self.rating = (self.rating * self.total_reviews + new_rating) / (self.total_reviews + 1)
        self.total_reviews += 1

class Review(db.Model):
    """Model for professional reviews"""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    is_visible = db.Column(db.Boolean, default=True)
    
    # Foreign Keys
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id', ondelete='CASCADE'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Relationships
    professional = db.relationship('Professional', back_populates='reviews')
    client = db.relationship('User', back_populates='reviews_given')
    
    def __repr__(self):
        return f"<Review {self.rating} for Professional {self.professional_id}>"
    
    def to_dict(self):
        """Convert review to dictionary"""
        return {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat(),
            'client_name': self.client.get_full_name() if self.client else 'Anonymous',
            'client_avatar': self.client.profile_picture if self.client else None
        }

# --------------------------
# Service Model
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
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Foreign Keys
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id', ondelete='CASCADE'), nullable=True)
    
    # Relationships with back_populates
    provider = db.relationship('User', back_populates='services')
    professional = db.relationship('Professional', 
                                 back_populates='services',
                                 foreign_keys=[professional_id])
    bookings = db.relationship('Booking', back_populates='service', lazy=True, cascade='all, delete-orphan')
    
    # Indexes for better query performance
    __table_args__ = (
        db.Index('idx_service_provider', 'provider_id'),
        db.Index('idx_service_professional', 'professional_id'),
        db.Index('idx_service_category', 'category'),
        db.Index('idx_service_active', 'is_active')
    )
    
    def __repr__(self):
        return f"<Service {self.title} - {self.category}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'location': self.location,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

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
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    # Foreign Keys
    client_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id', ondelete='CASCADE'), nullable=False)
    
    # Relationships
    client = db.relationship('User', back_populates='bookings')
    service = db.relationship('Service', back_populates='bookings')
    payment = db.relationship('Payment', back_populates='booking', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Booking {self.id} - {self.status}>"

    def __repr__(self):
        return f"<Booking {self.id} - {self.status}>"

# --------------------------
# Job Model
# --------------------------
class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    profession = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    location_lat = db.Column(db.Float, nullable=True)
    location_lng = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='open')  # open, in_progress, completed, cancelled
    budget = db.Column(db.Float, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Relationships
    poster = db.relationship('User', back_populates='job_postings')
    ai_suggestions = db.relationship('AISuggestion', back_populates='job', lazy=True, cascade='all, delete-orphan')

    def create_ai_suggestions(self, matches):
        """
        Create AI suggestions for matched professionals.
        
        Args:
            matches (list): List of match dictionaries containing 'professional', 'score', 
                          'similarity', 'distance_score', and 'distance_km' keys
        """
        from sqlalchemy.exc import SQLAlchemyError

        try:
            # Create all suggestions first
            suggestions = []
            for match in matches:
                suggestions.append(AISuggestion(
                    job_id=self.id,
                    professional_id=match["professional"].id,
                    score=match["score"],
                    similarity_score=match["similarity"],
                    distance_score=match["distance_score"],
                    distance_km=match["distance_km"]
                ))
            
            # Add all suggestions in a single operation
            db.session.bulk_save_objects(suggestions)
            db.session.commit()
            return True, f"Successfully created {len(suggestions)} suggestions"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            # Log the error or handle it appropriately
            return False, f"Failed to create suggestions: {str(e)}"

    def __repr__(self):
        return f'<Job {self.title}>'

# --------------------------
# AI Suggestion Model
# --------------------------
class AISuggestion(db.Model):
    __tablename__ = 'ai_suggestions'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Float, nullable=False)  # Match score (0-1)
    distance_km = db.Column(db.Float, nullable=True)  # Distance in kilometers
    similarity_score = db.Column(db.Float, nullable=True)  # Text similarity score
    distance_score = db.Column(db.Float, nullable=True)  # Distance-based score
    is_contacted = db.Column(db.Boolean, default=False)  # If the professional was contacted
    is_interested = db.Column(db.Boolean, default=None, nullable=True)  # Professional's interest status
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    job = db.relationship('Job', back_populates='ai_suggestions')
    professional = db.relationship('Professional', back_populates='ai_suggestions')
    
    def __repr__(self):
        return f'<AISuggestion Job:{self.job_id} Pro:{self.professional_id} Score:{self.score:.2f}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'professional_id': self.professional_id,
            'score': self.score,
            'distance_km': self.distance_km,
            'similarity_score': self.similarity_score,
            'distance_score': self.distance_score,
            'is_contacted': self.is_contacted,
            'is_interested': self.is_interested,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'professional': {
                'id': self.professional.id,
                'name': self.professional.full_name,
                'profession': self.professional.profession,
                'rating': self.professional.rating,
                'total_reviews': self.professional.total_reviews,
                'hourly_rate': self.professional.hourly_rate,
                'years_experience': self.professional.years_experience,
                'skills': self.professional.get_skills_list() if hasattr(self.professional, 'get_skills_list') else []
            } if self.professional else None
        }

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
    payment_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    # Foreign Key
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False)
    
    # Relationship
    booking = db.relationship('Booking', back_populates='payment')
    
    def __repr__(self):
        return f"<Payment {self.id} - {self.status}>"

    def __repr__(self):
        return f"<Payment {self.id} - {self.status}>"

