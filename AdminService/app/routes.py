from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import requests
from .models import ParkingSpot, ParkingAnnotation
from .extensions import db
from .utils import start_parking_annotation_process

admin_bp = Blueprint('admin', __name__)


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