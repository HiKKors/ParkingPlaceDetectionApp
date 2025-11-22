from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps

def roles_required(*required_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_roles = claims.get('roles', [])
            if not any(role in user_roles for role in required_roles):
                return jsonify(msg='Access forbidden: insufficient role'), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper