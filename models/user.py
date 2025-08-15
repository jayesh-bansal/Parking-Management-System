from flask_login import UserMixin
from models.database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin):
    def __init__(self, id, username, email, role, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.created_at = created_at

    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        
        if user_data:
            created_at = user_data['created_at']
            if isinstance(created_at, str):
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            return User(user_data['id'], user_data['username'], user_data['email'], user_data['role'], created_at)
        return None

    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        user_data = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user_data:
            created_at = user_data['created_at']
            if isinstance(created_at, str):
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            return User(user_data['id'], user_data['username'], user_data['email'], user_data['role'], created_at)
        return None

    @staticmethod
    def create_user(username, email, password, role='user'): # Keep role parameter with default 'user'
        conn = get_db_connection()
        password_hash = generate_password_hash(password)
        
        try:
            conn.execute('''
                INSERT INTO users (username, password_hash, email, role)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, email, role))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            conn.close()
            return False

    @staticmethod
    def verify_password(username, password):
        conn = get_db_connection()
        user_data = conn.execute('SELECT password_hash FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user_data:
            return check_password_hash(user_data['password_hash'], password)
        return False

    @staticmethod
    def get_all_users():
        conn = get_db_connection()
        users_data = conn.execute('SELECT * FROM users').fetchall()
        conn.close()
        
        users = []
        for user_data in users_data:
            created_at = user_data['created_at']
            if isinstance(created_at, str):
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            users.append(User(user_data['id'], user_data['username'], user_data['email'], user_data['role'], created_at))
        return users

    @staticmethod
    def user_exists(username, email):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email)).fetchone()
        conn.close()
        return user is not None

    @staticmethod
    def update_user_role(user_id, new_role):
        conn = get_db_connection()
        try:
            conn.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating user role: {e}")
            conn.close()
            return False
