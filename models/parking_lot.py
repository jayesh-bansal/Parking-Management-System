from models.database import get_db_connection

class ParkingLot:
    def __init__(self, id, prime_location_name, price, address, pin_code, maximum_number_of_spots, created_at):
        self.id = id
        self.prime_location_name = prime_location_name
        self.price = price
        self.address = address
        self.pin_code = pin_code
        self.maximum_number_of_spots = maximum_number_of_spots
        self.created_at = created_at

    @staticmethod
    def get_all():
        conn = get_db_connection()
        lots = conn.execute('''
            SELECT pl.*, 
                   COUNT(ps.id) AS total_spots,
                   CAST(SUM(CASE WHEN ps.status = 'A' THEN 1 ELSE 0 END) AS INTEGER) AS available_spots,
                   CAST(SUM(CASE WHEN ps.status = 'O' THEN 1 ELSE 0 END) AS INTEGER) AS occupied_spots
            FROM parking_lots pl
            LEFT JOIN parking_spots ps ON pl.id = ps.lot_id
            GROUP BY pl.id
        ''').fetchall()
        conn.close()
        return lots

    @staticmethod
    def get_by_id(lot_id):
        conn = get_db_connection()
        lot = conn.execute('SELECT * FROM parking_lots WHERE id = ?', (lot_id,)).fetchone()
        conn.close()
        return lot

    @staticmethod
    def create(location_name, price, address, pin_code, max_spots):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create parking lot
        cursor.execute('''
            INSERT INTO parking_lots (prime_location_name, price, address, pin_code, maximum_number_of_spots)
            VALUES (?, ?, ?, ?, ?)
        ''', (location_name, price, address, pin_code, max_spots))
        
        lot_id = cursor.lastrowid
        
        # Create parking spots for this lot
        for i in range(1, max_spots + 1):
            cursor.execute('''
                INSERT INTO parking_spots (lot_id, spot_number, status)
                VALUES (?, ?, 'A')
            ''', (lot_id, i))
        
        conn.commit()
        conn.close()
        return lot_id

    @staticmethod
    def update(lot_id, location_name, price, address, pin_code, max_spots):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get current lot details to compare max_spots
        current_lot = cursor.execute('SELECT maximum_number_of_spots FROM parking_lots WHERE id = ?', (lot_id,)).fetchone()
        if not current_lot:
            conn.close()
            return False
        
        old_max_spots = current_lot['maximum_number_of_spots']

        cursor.execute('''
            UPDATE parking_lots
            SET prime_location_name = ?, price = ?, address = ?, pin_code = ?, maximum_number_of_spots = ?
            WHERE id = ?
        ''', (location_name, price, address, pin_code, max_spots, lot_id))

        # Adjust parking spots if max_spots changed
        if max_spots > old_max_spots:
            for i in range(old_max_spots + 1, max_spots + 1):
                cursor.execute('''
                    INSERT INTO parking_spots (lot_id, spot_number, status)
                    VALUES (?, ?, 'A')
                ''', (lot_id, i))
        elif max_spots < old_max_spots:
            cursor.execute('''
                DELETE FROM parking_spots
                WHERE lot_id = ? AND spot_number > ? AND status = 'A'
            ''', (lot_id, max_spots))

        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete(lot_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if there are any occupied spots in this lot
            occupied_spots_count = cursor.execute(
                'SELECT COUNT(*) FROM parking_spots WHERE lot_id = ? AND status = "O"', 
                (lot_id,)
            ).fetchone()[0]

            if occupied_spots_count > 0:
                conn.close()
                return False

            cursor.execute('DELETE FROM reservations WHERE spot_id IN (SELECT id FROM parking_spots WHERE lot_id = ?)', (lot_id,))
            cursor.execute('DELETE FROM parking_spots WHERE lot_id = ?', (lot_id,))
            cursor.execute('DELETE FROM parking_lots WHERE id = ?', (lot_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting parking lot: {e}")
            conn.close()
            return False

    @staticmethod
    def get_available_lots():
        conn = get_db_connection()
        lots = conn.execute('''
            SELECT pl.*, 
                   COUNT(ps.id) as total_spots,
                   SUM(CASE WHEN ps.status = 'A' THEN 1 ELSE 0 END) as available_spots
            FROM parking_lots pl
            LEFT JOIN parking_spots ps ON pl.id = ps.lot_id
            GROUP BY pl.id
            HAVING available_spots > 0
        ''').fetchall()
        conn.close()
        return lots

    @staticmethod
    def get_spots_by_lot_id(lot_id):
        conn = get_db_connection()
        spots = conn.execute('''
            SELECT ps.*, r.user_id, r.parking_timestamp, u.username
            FROM parking_spots ps
            LEFT JOIN reservations r ON ps.id = r.spot_id AND r.status = 'active'
            LEFT JOIN users u ON r.user_id = u.id
            WHERE ps.lot_id = ?
            ORDER BY ps.spot_number
        ''', (lot_id,)).fetchall()
        conn.close()
        return spots

    @staticmethod
    def search_lots(query):
        conn = get_db_connection()
        # Use LIKE for partial matches and % for wildcards
        search_term = f"%{query}%"
        lots = conn.execute('''
            SELECT pl.*, 
                   COUNT(ps.id) AS total_spots,
                   CAST(SUM(CASE WHEN ps.status = 'A' THEN 1 ELSE 0 END) AS INTEGER) AS available_spots,
                   CAST(SUM(CASE WHEN ps.status = 'O' THEN 1 ELSE 0 END) AS INTEGER) AS occupied_spots
            FROM parking_lots pl
            LEFT JOIN parking_spots ps ON pl.id = ps.lot_id
            WHERE pl.prime_location_name LIKE ? OR pl.address LIKE ? OR pl.pin_code LIKE ?
            GROUP BY pl.id
            ORDER BY pl.prime_location_name
        ''', (search_term, search_term, search_term)).fetchall()
        conn.close()
        return lots
