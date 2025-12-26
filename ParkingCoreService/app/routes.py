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
    parking_logger.info('Opened all parkings page')
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

# @parking_bp.route('/addToFavorites', methods=["POST"])
# def add_to_favorites():
#     current_user_id = get_jwt_identity()['public_id']
#     data = request.get_json()
#     parking_spot_id = data.get('parking_spot_id')
    
#     if not parking_spot_id:
#         return jsonify({'error': 'parking_spot_id required'}), 400
    
#     # проверяем не добавлено ли уже в избранное
#     existing = FavoriteParking.query.filter_by(
#         user_id = current_user_id,
#         parking_spot_id = parking_spot_id
#     ).first()
    
#     if existing:
#         return jsonify({'msg': 'Парковка уже добавлена в избранное'}), 200
    
#     favorite = FavoriteParking(
#         user_id = current_user_id,
#         parking_spot_id = parking_spot_id
#     )
    
#     db.session.add(favorite)
#     db.session.commit()
    
#     return jsonify({'msg': 'Добавлено в избранное'}), 201

@parking_bp.route('/addToFavorites', methods=["POST"])
# @jwt_required()
def add_to_favorites():
    print()
    # user = get_jwt_identity()

    # current_user_id = user["public_id"]

    data = request.get_json()
    parking_spot_id = data.get("parking_spot_id")

    if not parking_spot_id:
        return jsonify({'error': 'parking_spot_id required'}), 400

    # existing = FavoriteParking.query.filter_by(
    #     user_id=current_user_id,
    #     parking_spot_id=parking_spot_id
    # ).first()

    # if existing:
    #     return jsonify({'msg': 'Парковка уже добавлена в избранное'}), 200

    favorite = FavoriteParking(
        user_id=8,
        parking_spot_id=parking_spot_id
    )

    db.session.add(favorite)
    db.session.commit()

    return jsonify({'msg': 'Добавлено в избранное'}), 201


@parking_bp.route('/spaces/<int:parkingId>', methods=['GET'])
def get_space(parkingId):
    parking_logger.info('Opened parking annotation page')
    
    space = ParkingSpot.query.get_or_404(parkingId)
    annotation = ParkingAnnotation.query.filter_by(parking_spot_id=parkingId).all()
    
    return render_template('parking_annotation.html', space=space, annotation=annotation)
        
    # return jsonify(space=space, annotation=annotation)
    
@parking_bp.route('/spaces/7', methods=['GET'])
def parking_test():
    return render_template('parking_schema.html', numbers=range(1, 11))

@parking_bp.route('/favorites', methods=['GET'])
def my_favorites():
    if request.method == 'GET':
        current_user_id = 8
        favorites = FavoriteParking.query.filter_by(user_id=current_user_id).all()
        
        fav_parkings = []
        
        for favorite in favorites:
            parking_spot = ParkingSpot.query.get(favorite.parking_spot_id)
            fav_parkings.append(parking_spot)
        
        return render_template('favorite_parkings.html', favorites=fav_parkings)
    

