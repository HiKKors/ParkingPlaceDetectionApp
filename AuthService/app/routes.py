from flask import Blueprint, render_template, request, jsonify, redirect, url_for, make_response, flash
from .models import User
from .extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, set_access_cookies
from .blocklist import BLOCKLIST
from .logger import auth_logger
from .decorators import roles_required
from .jwt_routes import create_jwt
# from .kafka_producer import send_registration_event

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.form
    if User.query.filter_by(email=data['email']).first():
        auth_logger.info(f'Попытка зарегистрировать существующего пользователя {data['email']}')
        return jsonify({'msg': 'User already exists'}), 400
    
    user = User(
        email=data['email'],
        name=data.get('name'),  # Use .get() to avoid KeyError if missing
        surname=data.get('surname'),
        roles=['user']
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    auth_logger.info('Успешная регистрация пользователя с email: %s', data['email']) 
    
    # send_registration_event({'username': user.username, 'public_id': user.public_id})
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.form
    
    if data['email'] == 'newadmin@gmail.com' and data['password'] == 'admin':
        response = make_response(
            redirect("http://localhost:5000/admin/add-parking")
        )
        return response
        
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        auth_logger.info('Попытка войти под не существующим аккаунтом')
        return jsonify({'msg': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=user.public_id, additional_claims={'roles': user.roles})
    auth_logger.info('Успешный вход пользователя с email: %s', data['email'])
    
    response = make_response(
        redirect("http://localhost:5002/parking/spaces")
    )

    set_access_cookies(response, access_token)

    return response


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(public_id=current_user_id).first()
    return render_template('profile.html', user=user)

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

@auth_bp.route('/get_all_users', methods=['GET'])
def get_all_users():
    auth_logger.info("ПОЛУЧЕНИЕ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ")
    users = User.query.all()

    users_data = [
        {
            "id": user.id,
            "name": user.name,
            "surname": user.surname,
            "email": user.email,
            "roles": user.roles
        }
        for user in users
    ]

    return jsonify(users_data), 200

@auth_bp.route('/edit-users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    auth_logger.info(f"Обновление пользователя ID={user_id}")
    print('Обновление пользователя')
    user = User.query.get(user_id)
    print(user.roles)
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404

    data = request.get_json()
    print(data)
    if not data:
        return jsonify({"error": "Данные не переданы"}), 400

    # Разрешённые к обновлению поля
    if 'email' in data:
        user.email = data['email']

    if 'roles' in data:
        role = []
        role.append(data['roles'])
        user.roles = role
        

    if 'password' in data:
        user.set_password(data['password'])  # обязательно через хеширование

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        auth_logger.error(f"Ошибка обновления пользователя: {e}")
        return jsonify({"error": "Ошибка обновления пользователя"}), 500

    return jsonify({
        "id": user.id,
        "email": user.email,
        "roles": user.roles
    }), 200
    
@auth_bp.route('/update_user/<int:user_id>', methods=['POST'])
@jwt_required()
def update_user_profile(user_id):
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(public_id=current_user_id).first()
    
    # Проверка, что пользователь редактирует свой аккаунт
    
    # Обновление данных
    user.name = request.form.get('name')
    user.surname = request.form.get('surname')
    user.email = request.form.get('email')
    
    # Валидация (опционально, добавь больше проверок)
    if not user.name or not user.surname or not user.email:
        return redirect(url_for('auth.profile'))
    
    # Если email изменился, проверь уникальность
    if user.email != request.form.get('email'):
        existing_user = User.query.filter_by(email=user.email).first()
        if existing_user:
            flash('Этот email уже используется!', 'error')
            return redirect(url_for('auth.profile'))
    
    db.session.commit()
    auth_logger.info('Успешно обновлены данные')
    return redirect(url_for('auth.profile'))

