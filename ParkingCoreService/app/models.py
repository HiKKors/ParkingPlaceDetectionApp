from .extensions import db
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(256), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class ParkingAnnotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parking_spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    file_path = db.Column(db.String(256), nullable=False) # путь к json файлу с разметкой
    # annotation_data = db.Column(JSONB, nullable=True)      # или можно хранить сам JSON в базе
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    parking_spot = db.relationship('ParkingSpot', back_populates='annotations')
    
class FavoriteParkings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'parking_spot_id', name='unique_favorite_per_user'),
    )