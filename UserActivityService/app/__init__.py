from flask import Flask
from .extensions import db
from .routes import user_activity_bp
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    # jwt.init_app(app)
    
    app.register_blueprint(user_activity_bp, url_prefix='/user-activity')
    
    with app.app_context():
        db.create_all()
        
    return app