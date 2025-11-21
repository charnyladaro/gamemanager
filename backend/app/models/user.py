from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100))
    avatar_url = db.Column(db.String(255))
    is_online = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    games = db.relationship('UserGame', back_populates='user', cascade='all, delete-orphan')
    sent_requests = db.relationship('Friendship', foreign_keys='Friendship.user_id',
                                   back_populates='user', cascade='all, delete-orphan')
    received_requests = db.relationship('Friendship', foreign_keys='Friendship.friend_id',
                                       back_populates='friend', cascade='all, delete-orphan')
    game_requests = db.relationship('GameRequest', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_email=False, include_admin=False):
        data = {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name or self.username,
            'avatar_url': self.avatar_url,
            'is_online': self.is_online,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'created_at': self.created_at.isoformat()
        }
        if include_email:
            data['email'] = self.email
        if include_admin:
            data['is_admin'] = self.is_admin
        return data
