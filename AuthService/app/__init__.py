from flask import Flask
from .extensions import db, jwt
from .routes import auth_bp
from config import Config
from flask_migrate import Migrate
# from flask_cors import CORS

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    # CORS(app, resources={r"/*": {"origins": "*"}})
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    with app.app_context():
        db.create_all()
        
    return app