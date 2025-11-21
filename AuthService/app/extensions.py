from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
# from .models import User
from .blocklist import BLOCKLIST

db = SQLAlchemy()
jwt = JWTManager()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in BLOCKLIST