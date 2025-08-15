from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models.parking_lot import ParkingLot
from models.reservation import Reservation

api_bp = Blueprint('api', __name__)

@api_bp.route('/parking_stats')
@login_required
def parking_stats():
    if current_user.role == 'admin':
        # Admin stats
        lots = ParkingLot.get_all()
        
        stats = {
            'labels': [lot['prime_location_name'] for lot in lots],
            'available': [lot['available_spots'] or 0 for lot in lots],
            'occupied': [lot['occupied_spots'] or 0 for lot in lots]
        }
    else:
        # User stats
        user_stats = Reservation.get_user_stats(current_user.id)
        
        stats = {
            'labels': [stat['date'] for stat in user_stats],
            'bookings': [stat['bookings'] for stat in user_stats]
        }
    
    return jsonify(stats)
