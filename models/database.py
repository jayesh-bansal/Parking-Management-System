import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'parking_app.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Parking lots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prime_location_name TEXT NOT NULL,
            price REAL NOT NULL,
            address TEXT NOT NULL,
            pin_code TEXT NOT NULL,
            maximum_number_of_spots INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Parking spots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_spots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_id INTEGER NOT NULL,
            spot_number INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'A',
            FOREIGN KEY (lot_id) REFERENCES parking_lots (id),
            UNIQUE(lot_id, spot_number)
        )
    ''')
    
    # Reservations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spot_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            parking_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            leaving_timestamp TIMESTAMP NULL,
            parking_cost REAL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'active',
            FOREIGN KEY (spot_id) REFERENCES parking_spots (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create admin user if not exists
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', admin_password, 'admin@parking.com', 'admin'))
    
    conn.commit()
    conn.close()
