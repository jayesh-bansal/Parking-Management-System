from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.parking_lot import ParkingLot
from models.user import User
from models.reservation import Reservation
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied!', 'error')
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    parking_lots = ParkingLot.get_all()
    print(parking_lots)
    return render_template('admin_dashboard.html', 
                           parking_lots=parking_lots)

@admin_bp.route('/summary')
@login_required
@admin_required
def summary():
    # This page will show the summary statistics and charts
    parking_lots = ParkingLot.get_all() # Needed to get total lots for summary card
    total_users = len(User.get_all_users())
    active_reservations = Reservation.get_active_count()
    
    return render_template('admin_summary.html', 
                           total_parking_lots=len(parking_lots), # Pass count directly
                           total_users=total_users,
                           active_reservations=active_reservations)

@admin_bp.route('/search_lots', methods=['GET'])
@login_required
@admin_required
def search_lots():
    query = request.args.get('query', '').strip()
    search_results = []
    if query:
        search_results = ParkingLot.search_lots(query)
    
    return render_template('admin_search_lots.html', 
                           search_results=search_results, 
                           query=query)

@admin_bp.route('/create_lot', methods=['GET', 'POST'])
@login_required
@admin_required
def create_lot():
    if request.method == 'POST':
        location_name = request.form['location_name']
        price = float(request.form['price'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        max_spots = int(request.form['max_spots'])
        
        lot_id = ParkingLot.create(location_name, price, address, pin_code, max_spots)
        
        if lot_id:
            flash(f'Parking lot "{location_name}" created successfully with {max_spots} spots!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Failed to create parking lot!', 'error')
    
    return render_template('create_lot.html')

@admin_bp.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lot(lot_id):
    lot = ParkingLot.get_by_id(lot_id)
    if not lot:
        flash('Parking lot not found!', 'error')
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        location_name = request.form['location_name']
        price = float(request.form['price'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        max_spots = int(request.form['max_spots'])

        if ParkingLot.update(lot_id, location_name, price, address, pin_code, max_spots):
            flash(f'Parking lot "{location_name}" updated successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Failed to update parking lot!', 'error')
    
    return render_template('edit_lot.html', lot=lot)

@admin_bp.route('/delete_lot/<int:lot_id>', methods=['POST'])
@login_required
@admin_required
def delete_lot(lot_id):
    if ParkingLot.delete(lot_id):
        flash('Parking lot deleted successfully!', 'success')
    else:
        flash('Failed to delete parking lot. It might have active reservations or occupied spots.', 'error')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/view_lot/<int:lot_id>')
@login_required
@admin_required
def view_lot(lot_id):
    lot = ParkingLot.get_by_id(lot_id)
    spots = ParkingLot.get_spots_by_lot_id(lot_id)
    
    # Prepare spot_reservations for view_spots.html
    spot_reservations = {}
    for spot in spots:
        if spot['user_id']: # If there's an active reservation for this spot
            # Create dummy objects for nested access in template
            class DummyParkingSpot:
                def __init__(self, spot_number, parking_lot):
                    self.spot_number = spot_number
                    self.parking_lot = parking_lot
            class DummyParkingLot:
                def __init__(self, prime_location_name, price):
                    self.prime_location_name = prime_location_name
                    self.price = price
            class DummyUser:
                def __init__(self, username):
                    self.username = username

            r_dict = dict(spot) # Convert Row object to dict
            if isinstance(r_dict['parking_timestamp'], str):
                r_dict['parking_timestamp'] = datetime.strptime(r_dict['parking_timestamp'], '%Y-%m-%d %H:%M:%S')
            
            r_dict['parking_spot'] = DummyParkingSpot(r_dict['spot_number'], DummyParkingLot(lot['prime_location_name'], lot['price']))
            r_dict['user'] = DummyUser(r_dict['username'])
            
            spot_reservations[spot['id']] = type('ReservationObject', (object,), r_dict)()

    return render_template('view_spots.html', 
                           lot=lot, 
                           spots=spots, 
                           spot_reservations=spot_reservations,
                           moment=datetime # Pass datetime as 'moment' to the template
                          )

@admin_bp.route('/users')
@login_required
@admin_required
def view_users():
    users = User.get_all_users()
    return render_template('admin_users.html', users=users)

@admin_bp.route('/update_user_role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    new_role = request.form.get('role')
    user_to_update = User.get_by_id(user_id)

    if not user_to_update:
        flash('User not found!', 'error')
        return redirect(url_for('admin.view_users'))

    if new_role not in ['user', 'admin']:
        flash('Invalid role specified!', 'error')
        return redirect(url_for('admin.view_users'))

    if User.update_user_role(user_id, new_role):
        flash(f'Role for {user_to_update.username} updated to {new_role}!', 'success')
    else:
        flash(f'Failed to update role for {user_to_update.username}.', 'error')
    
    return redirect(url_for('admin.view_users'))
