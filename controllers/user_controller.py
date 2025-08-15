from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.parking_lot import ParkingLot
from models.reservation import Reservation
from datetime import datetime # Added this import to fix NameError

user_bp = Blueprint('user', __name__)

def user_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'user':
            flash('Access denied!', 'error')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@user_bp.route('/dashboard')
@login_required
@user_required
def dashboard():
    available_lots = ParkingLot.get_available_lots()
    current_reservations = Reservation.get_user_active_reservations(current_user.id)
    parking_history = Reservation.get_user_history(current_user.id)
    
    # Prepare lot_availability for the template
    lot_availability = {lot['id']: lot['available_spots'] for lot in available_lots}

    return render_template('user_dashboard.html',
                           available_lots=available_lots,
                           current_reservations=current_reservations,
                           parking_history=parking_history,
                           lot_availability=lot_availability,
                           moment=datetime # Pass datetime for utcnow() in template
                          )

@user_bp.route('/book_spot/<int:lot_id>', methods=['POST'])
@login_required
@user_required
def book_spot(lot_id):
    if Reservation.book_spot(lot_id, current_user.id):
        flash('Parking spot booked successfully!', 'success')
    else:
        flash('No available spots in this parking lot!', 'error')
    
    return redirect(url_for('user.dashboard'))

@user_bp.route('/release_spot/<int:reservation_id>', methods=['POST'])
@login_required
@user_required
def release_spot(reservation_id):
    success, cost = Reservation.release_spot(reservation_id, current_user.id)
    
    if success:
        flash(f'Parking spot released! Total cost: ${cost:.2f}', 'success')
    else:
        flash('Invalid reservation!', 'error')
    
    return redirect(url_for('user.dashboard'))
