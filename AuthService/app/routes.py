from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from .models import User
from .extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from .blocklist import BLOCKLIST
from .logger import auth_logger
from .decorators import roles_required
from .kafka_producer import send_registration_event

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.form
    if User.query.filter_by(username=data['username']).first():
        auth_logger.info(f'Попытка зарегистрировать существующего пользователя {data['username']}')
        return jsonify({'msg': 'User already exists'}), 400
    
    user = User(username=data['username'], roles=['user'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    auth_logger.info('Успешная регистрация пользователя с username: %s', data['username']) 
    
    # send_registration_event({'username': user.username, 'public_id': user.public_id})
    
    return jsonify({'msg': 'User creted successfully'}), 201

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.form
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        auth_logger.info('Попытка войти под не существующим аккаунтом')
        return jsonify({'msg': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=user.public_id, additional_claims={'roles': user.roles})
    auth_logger.info('Успешный вход пользователя с username: %s', data['username'])
    return jsonify({'msg': 'Login successful', 'access_token': access_token}), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(public_id=current_user_id).first()
    return render_template('profile.html', username=user.username, public_id=user.public_id)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # JWT ID уникальный идентификатор токена
    BLOCKLIST.add(jti)       # Добавляем токен в черный список
    response = redirect(url_for('auth.login'))
    return {"msg": "Successfully logged out"}, 200

@auth_bp.route('/admin', methods=['GET'])
@roles_required('admin')
def admin_area():
    return jsonify(msg="Welcome admin!")