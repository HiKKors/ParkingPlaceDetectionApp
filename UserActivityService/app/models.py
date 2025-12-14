from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from .extensions import db

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    rating = db.Column(db.Integer)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)