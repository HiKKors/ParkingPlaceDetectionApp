from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import requests
from .models import ParkingSpot, ParkingAnnotation
from .extensions import db
from .utils import start_parking_annotation_process, get_coordinates
import time
from flask import request, jsonify
from werkzeug.utils import secure_filename
import os

admin_bp = Blueprint('admin', __name__)

UPLOAD_DIR = "../videos"


@admin_bp.route('/add-parking', methods=['GET', "POST"])
def add_parking():
    if request.method == 'GET':
        return render_template('add_parking.html')

    if request.method == 'POST':
        data = request.json

        parking = ParkingSpot(
            address=data['address'],
            price_per_hour=data['price_per_hour'],
            lat=data['lat'],
            lon=data['lon']
        )
        
        db.session.add(parking)
        db.session.commit()
        return jsonify({'id': parking.id, 'message': 'Парковка добавлена успешно'}), 201
    
@admin_bp.route('/parkings', methods=['GET'])
def get_parkings():
    spots = ParkingSpot.query.all()
    result = []
    for spot in spots:
        # Геокодируем адрес в координаты (если их нет)
        coords = get_coordinates(spot.address)  # ваша функция геокодера
        result.append({
            'id': spot.id,
            'address': spot.address,
            'price_per_hour': spot.price_per_hour,
            'lat': coords[0],
            'lon': coords[1]
        })
    return jsonify(result)
    
@admin_bp.route('/parking/<int:parking_id>/start-annotation', methods=['POST'])
def start_annotation(parking_id):
    parking = ParkingSpot.query.get_or_404(parking_id)

    start_parking_annotation_process(parking)

    return jsonify({
        'message': 'Процесс разметки запущен'
    }), 202
    
@admin_bp.route('/parking/<int:parking_id>/save-annotation', methods=['POST'])
def save_parking_annotation(parking_id):
    parking = ParkingSpot.query.get_or_404(parking_id)

    payload = request.json
    if not payload:
        return jsonify({'error': 'Нет данных разметки'}), 400

    annotation = ParkingAnnotation(
        parking_spot_id=parking.id,
        file_path=payload['file_path'],
        annotation_data=payload['annotation_data'],
        created_at=datetime.utcnow()
    )

    db.session.add(annotation)
    db.session.commit()

    return jsonify({'message': 'Разметка сохранена'}), 200

@admin_bp.route('/parking/<int:parking_id>/upload-video', methods=['GET', 'POST'])
def add_video(parking_id):
    if 'video' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'Пустое имя файла'}), 400

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_DIR, f"parking_{parking_id}_{filename}")
    file.save(save_path)

    time.sleep(3)  # как будто OpenCV + ultralytics

    return jsonify({
        'message': 'Видео успешно обработано',
        'video_path': save_path
    }), 200
    
@admin_bp.route('/user_managment', methods=['GET', 'POST'])
def user_list():
    if request.method == 'GET':
        response = requests.get('http://localhost:5001/auth/get_all_users')
        users = response.json()
        return render_template('user_managment.html', users=users)
    
@admin_bp.route('/user_managment/<int:user_id>/update', methods=['POST'])
def admin_update_user(user_id):
    data = request.form.to_dict()

    if not data:
        return "Данные не переданы", 400

    try:
        response = requests.put(
            f'http://localhost:5001/auth/edit-users/{user_id}',
            json=data,
            timeout=5
        )
    except requests.RequestException as e:
        return "Сервис авторизации недоступен", 503

    if response.status_code != 200:
        return response.json(), response.status_code

    return redirect(url_for('admin.user_list'))

@admin_bp.route('/delete_parking/<int:parkingId>', methods=['DELETE'])
def delete_parking(parkingId):
    parking = ParkingSpot.query.filter_by(id=parkingId).first()

    if not parking:
        return jsonify({'error': 'Парковка не найдена'}), 404

    db.session.delete(parking)
    db.session.commit()

    return jsonify({'message': 'Парковка удалена'})

@admin_bp.route('/parking/<int:parking_id>', methods=['PUT'])
def update_parking(parking_id):
    parking = ParkingSpot.query.get(parking_id)

    if not parking:
        return jsonify({'error': 'Парковка не найдена'}), 404

    data = request.get_json()

    parking.address = data.get('address', parking.address)
    parking.price_per_hour = data.get('price_per_hour', parking.price_per_hour)
    parking.lat = data.get('lat', parking.lat)
    parking.lon = data.get('lon', parking.lon)

    db.session.commit()

    return jsonify({'message': 'Парковка обновлена'})
