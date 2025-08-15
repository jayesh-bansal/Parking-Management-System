# Vehicle Parking Management App

A comprehensive Flask-based parking management system with proper MVC architecture.

## Project Structure

```
parking_app/
├── app.py                      # Main Flask application
├── models/                     # Database models
│   ├── database.py            # Database initialization
│   ├── user.py                # User model
│   ├── parking_lot.py         # Parking lot model
│   └── reservation.py         # Reservation model
├── controllers/               # Route controllers
│   ├── auth_controller.py     # Authentication routes
│   ├── admin_controller.py    # Admin routes
│   ├── user_controller.py     # User routes
│   └── api_controller.py      # API endpoints
├── templates/                 # Jinja2 templates
│   ├── base.html             # Base template
│   ├── index.html            # Home page
│   └── login.html            # Login page
├── static/                   # Static files
│   ├── images/ 
│       ├── car-entering-garage.jpeg                   # Images
│       ├── highlighted-parking-spot.jpeg              # Images
│       ├── indoor-parking-lights.jpeg                 # Images
│       └── outdoor-parking-lot-isometric.jpeg         # Images
│   └── css/
│       └── style.css         # Custom styles
├── app.py                    # Configuration setting
├── openapi.yaml              # Defines the structure and endpoints of the RESTful API
└── requirements.txt          # Python dependencies
```

## Installation and Running the Application

To run this application, you need to have Python and pip installed on your system.

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Initialize the database (if not already done):**
   If you're running for the first time or want to reset the database, delete the `parking_app.db` file from the project root, then proceed to step 3. The database will be recreated automatically.
3. **Run the application:**
   ```bash
   python app.py
   ```
4. **Access the application:** Open your web browser and go to `http://localhost:5000`.
5. **Stop the application:** Press `Ctrl+C` in your terminal.

## Default Admin Credentials
- Username: `admin`
- Password: `admin123`

## Features

### Admin Features
- Create/manage parking lots
- View all parking spots status
- Monitor user registrations
- View analytics and charts

### User Features
- Register and login
- Book available parking spots
- Release parking spots
- View parking history
- Personal analytics

## Technology Stack
- **Backend**: Flask, SQLite
- **Frontend**: Bootstrap 5, Chart.js
- **Authentication**: Flask-Login
- **Architecture**: MVC Pattern