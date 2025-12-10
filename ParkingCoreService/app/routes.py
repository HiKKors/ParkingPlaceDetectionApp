from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from .models import ParkingSpot, ParkingAnnotation, FavoriteParking
from .extensions import db
from .utils import get_coordinates
from .parking_logger import parking_logger
import numpy as np
import cv2
from flask_jwt_extended import get_jwt_identity, jwt_required

parking_bp = Blueprint('parking', __name__)


@parking_bp.route('/spaces', methods = ['GET'])
def get_spaces():
    return render_template('spaces.html')

@parking_bp.route('/parkings', methods=['GET'])
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

@parking_bp.route('/addToFavorites', methods=["POST"])
def add_to_favorites():
    current_user_id = get_jwt_identity()['public_id']
    data = request.get_json()
    parking_spot_id = data.get('parking_spot_id')
    
    if not parking_spot_id:
        return jsonify({'error': 'parking_spot_id required'}), 400
    
    # проверяем не добавлено ли уже в избранное
    existing = FavoriteParking.query.filter_by(
        user_id = current_user_id,
        parking_spot_id = parking_spot_id
    ).first()
    
    if existing:
        return jsonify({'msg': 'Парковка уже добавлена в избранное'}), 200
    
    favorite = FavoriteParking(
        user_id = current_user_id,
        parking_spot_id = parking_spot_id
    )
    
    db.session.add(favorite)
    db.session.commit()
    
    return jsonify({'msg': 'Добавлено в избранное'}), 201