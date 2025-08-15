from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
import os
from models.database import init_db
from controllers.auth_controller import auth_bp
from controllers.admin_controller import admin_bp
from controllers.user_controller import user_bp
from controllers.api_controller import api_bp
from models.user import User
from config import config

app = Flask(__name__)

config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

print(f"Running in {config_name} mode")
print(f"SECRET_KEY length: {len(app.config['SECRET_KEY'])}")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    return render_template('index.html')

if __name__ == '__main__':
    try:
        print("Attempting to initialize database...")
        init_db()
        print("Database initialized successfully (or already exists).")
    except Exception as e:
        print(f"Error during database initialization: {e}")
    app.run(debug=True)
