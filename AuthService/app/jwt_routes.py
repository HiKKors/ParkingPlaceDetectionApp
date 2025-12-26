import jwt
from datetime import datetime, timedelta
from config import Config
from .models import User

def create_jwt(user):
    print(user.id)
    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": user.roles,
        "exp": datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRE_HOURS)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
