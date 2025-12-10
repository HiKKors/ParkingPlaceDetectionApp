# app/models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from .extensions import db

# db = SQLAlchemy()

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    lat = db.Column(db.Float, nullable=True)  # координаты
    lon = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Правильная связь один-ко-многим
    annotations = db.relationship('ParkingAnnotation', backref='parking_spot', lazy=True, cascade='all, delete-orphan')

class ParkingAnnotation(db.Model):
    __tablename__ = 'parking_annotations'

    id = db.Column(db.Integer, primary_key=True)
    parking_spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    annotation_data = db.Column(JSONB, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FavoriteParking(db.Model):
    __tablename__ = 'user_favorite_parkings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    parking_spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'parking_spot_id', name='unique_favorite_per_user'),
    )
