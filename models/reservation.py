from models.database import get_db_connection
from datetime import datetime
import math

class Reservation:
    @staticmethod
    def get_user_active_reservations(user_id):
        conn = get_db_connection()
        reservations_data = conn.execute('''
            SELECT r.*, ps.spot_number, pl.prime_location_name, pl.price
            FROM reservations r
            JOIN parking_spots ps ON r.spot_id = ps.id
            JOIN parking_lots pl ON ps.lot_id = pl.id
            WHERE r.user_id = ? AND r.status = 'active'
        ''', (user_id,)).fetchall()
        conn.close()
        
        reservations = []
        for r_data in reservations_data:
            r_dict = dict(r_data) # Convert Row object to dict for easier modification
            
            # Convert parking_timestamp to datetime object
            if isinstance(r_dict['parking_timestamp'], str):
                r_dict['parking_timestamp'] = datetime.strptime(r_dict['parking_timestamp'], '%Y-%m-%d %H:%M:%S')
            
            # leaving_timestamp might be NULL, so check before converting
            if r_dict['leaving_timestamp'] and isinstance(r_dict['leaving_timestamp'], str):
                r_dict['leaving_timestamp'] = datetime.strptime(r_dict['leaving_timestamp'], '%Y-%m-%d %H:%M:%S')

            # Create dummy objects for nested access in template (ParkingLot, ParkingSpot)
            class DummyParkingSpot:
                def __init__(self, spot_number, parking_lot):
                    self.spot_number = spot_number
                    self.parking_lot = parking_lot
            class DummyParkingLot:
                def __init__(self, prime_location_name, price):
                    self.prime_location_name = prime_location_name
                    self.price = price

            r_dict['parking_spot'] = DummyParkingSpot(r_dict['spot_number'], DummyParkingLot(r_dict['prime_location_name'], r_dict['price']))
            reservations.append(type('ReservationObject', (object,), r_dict)()) # Convert dict back to object-like
        return reservations

    @staticmethod
    def get_user_history(user_id, limit=10):
        conn = get_db_connection()
        history_data = conn.execute('''
            SELECT r.*, ps.spot_number, pl.prime_location_name, pl.price
            FROM reservations r
            JOIN parking_spots ps ON r.spot_id = ps.id
            JOIN parking_lots pl ON ps.lot_id = pl.id
            WHERE r.user_id = ?
            ORDER BY r.parking_timestamp DESC
            LIMIT ?
        ''', (user_id, limit)).fetchall()
        conn.close()
        
        history = []
        for h_data in history_data:
            h_dict = dict(h_data)
            
            # Convert parking_timestamp to datetime object
            if isinstance(h_dict['parking_timestamp'], str):
                h_dict['parking_timestamp'] = datetime.strptime(h_dict['parking_timestamp'], '%Y-%m-%d %H:%M:%S')
            
            # leaving_timestamp might be NULL, so check before converting
            if h_dict['leaving_timestamp'] and isinstance(h_dict['leaving_timestamp'], str):
                h_dict['leaving_timestamp'] = datetime.strptime(h_dict['leaving_timestamp'], '%Y-%m-%d %H:%M:%S')
            
            class DummyParkingSpot:
                def __init__(self, spot_number, parking_lot):
                    self.spot_number = spot_number
                    self.parking_lot = parking_lot
            class DummyParkingLot:
                def __init__(self, prime_location_name, price):
                    self.prime_location_name = prime_location_name
                    self.price = price

            h_dict['parking_spot'] = DummyParkingSpot(h_dict['spot_number'], DummyParkingLot(h_dict['prime_location_name'], h_dict['price']))
            history.append(type('ReservationObject', (object,), h_dict)())
        return history

    @staticmethod
    def book_spot(lot_id, user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find first available spot in the lot
        spot = cursor.execute('''
            SELECT id FROM parking_spots 
            WHERE lot_id = ? AND status = 'A' 
            ORDER BY spot_number 
            LIMIT 1
        ''', (lot_id,)).fetchone()
        
        if not spot:
            conn.close()
            return False
        
        spot_id = spot['id']
        
        # Create reservation
        cursor.execute('''
            INSERT INTO reservations (spot_id, user_id, status)
            VALUES (?, ?, 'active')
        ''', (spot_id, user_id))
        
        # Update spot status
        cursor.execute('''
            UPDATE parking_spots SET status = 'O' WHERE id = ?
        ''', (spot_id,))
        
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def release_spot(reservation_id, user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get reservation details
        reservation = cursor.execute('''
            SELECT r.*, pl.price FROM reservations r
            JOIN parking_spots ps ON r.spot_id = ps.id
            JOIN parking_lots pl ON ps.lot_id = pl.id
            WHERE r.id = ? AND r.user_id = ? AND r.status = 'active'
        ''', (reservation_id, user_id)).fetchone()
        
        if not reservation:
            conn.close()
            return False, 0
        
        # Calculate parking cost
        # Ensure parking_timestamp is a datetime object for calculation
        parking_start_str = reservation['parking_timestamp']
        parking_start = datetime.strptime(parking_start_str, '%Y-%m-%d %H:%M:%S')
        parking_end = datetime.utcnow() # Use UTC for consistency
        
        # Calculate hours, rounding up to the nearest whole hour, with a minimum of 1 hour
        hours_parked = max(1, math.ceil((parking_end - parking_start).total_seconds() / 3600))
        parking_cost = hours_parked * reservation['price']
        
        # Update reservation
        cursor.execute('''
            UPDATE reservations 
            SET leaving_timestamp = CURRENT_TIMESTAMP, 
                parking_cost = ?, 
                status = 'completed'
            WHERE id = ?
        ''', (parking_cost, reservation_id))
        
        # Update spot status
        cursor.execute('''
            UPDATE parking_spots SET status = 'A' WHERE id = ?
        ''', (reservation['spot_id'],))
        
        conn.commit()
        conn.close()
        return True, parking_cost

    @staticmethod
    def get_active_count():
        conn = get_db_connection()
        count = conn.execute('SELECT COUNT(*) as count FROM reservations WHERE status = "active"').fetchone()
        conn.close()
        return count['count']

    @staticmethod
    def get_user_stats(user_id):
        conn = get_db_connection()
        stats = conn.execute('''
            SELECT DATE(r.parking_timestamp) as date, COUNT(*) as bookings
            FROM reservations r
            WHERE r.user_id = ?
            GROUP BY DATE(r.parking_timestamp)
            ORDER BY date DESC
            LIMIT 7
        ''', (user_id,)).fetchall()
        conn.close()
        return stats
