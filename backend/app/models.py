from datetime import datetime
from app import db
from flask_bcrypt import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))  # Null for OAuth users
    name = db.Column(db.String(100))

    # OAuth fields
    oauth_provider = db.Column(db.String(50))  # 'google', 'okta', 'github', etc.
    oauth_id = db.Column(db.String(255))  # Provider's user ID
    avatar_url = db.Column(db.String(500))

    # Account info
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationship to flood reports
    reports = db.relationship('FloodReport', backref='user', lazy=True)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check if password matches hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_email=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'avatar_url': self.avatar_url,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_email:
            data['email'] = self.email
            data['email_verified'] = self.email_verified
            data['oauth_provider'] = self.oauth_provider
        return data


class FloodReport(db.Model):
    __tablename__ = 'flood_reports'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255))
    severity = db.Column(db.String(20), nullable=False)  # Low, Medium, High, Critical
    description = db.Column(db.Text)
    photo_url = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Active')  # Active, Resolved, Deleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, include_user=True):
        data = {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'severity': self.severity,
            'description': self.description,
            'photo_url': self.photo_url,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_user and self.user:
            data['user'] = self.user.to_dict()
        return data
