from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import requests 
import config

import logging
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

app.config.from_object(config.Config)


# Initialize database and other extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

with app.app_context():
    db.create_all()  # Create all defined tables

# Only after initializing `db` do we import `User`
from models import User, Plant, FavoritePlant, PlantCare, PlantDisease

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create all tables in the current app context
with app.app_context():
    db.create_all()  # Create all defined tables

# @app.route('/index') 
# def index_page():
#     return render_template('index.html')  


@app.route('/')
def index():
    return render_template('index.html') 



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        bio = request.form.get('bio', '')

        # Validation checks
        if not username or not email or not password:
            flash('Please fill in all required fields.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        # Hash password and create user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Choose another.', 'error')
            return render_template('register.html')

        new_user = User(username=username, email=email, password=hashed_password, bio=bio)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    # Render registration form for GET requests
    return render_template('register.html')


    


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        password = request.form.get('password')

        # Retrieve the user from the database by username
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode(), user.password):  # Check if the password matches
            login_user(user)  # Use Flask-Login to mark the user as logged in
            session['username'] = user.username  # Set session variable
            return redirect(url_for('profile', username=user.username))  # Redirect to user profile
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return redirect(url_for('login'))  # Return with error message

    return render_template('login.html')  # Render login form for GET requests

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Ensure Flask-Login logs out the user
    session.clear()  # Clear session data
    # Redirect to the login page or another desired page after logging out
    return redirect(url_for('login'))

@app.route('/profile/<username>', methods=['GET', 'POST'])
def manage_profile(username):
    # Retrieve user data from the database
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('User not found', 'error')

        print(f"Accessing profile for {username}")  # Debugging output

        return redirect(url_for('login'))  # Handle missing user profile

    if request.method == 'POST':
        # Handle profile update
        email = request.form.get('email')
        bio = request.form.get('bio')

        # Update user information in the database
        user.email = email
        user.bio = bio
        db.session.commit()  # Commit the changes to the database

        flash('Profile updated successfully.', 'success')

    # Render the profile page
    return render_template('profile.html', username=username, profile=user)  # Pass the user profile data

@app.route('/favorites', methods=['GET'])
@login_required
def view_favorites():
    favorites = FavoritePlant.query.filter_by(user_id=current_user.id).all()
    return render_template('favorites.html', favorites=favorites)

@app.route('/add_favorite/<int:plant_id>')
@login_required
def add_favorite(plant_id):
    favorite = FavoritePlant(user_id=current_user.id, plant_id=plant_id)
    db.session.add(favorite)
    db.session.commit()
    flash("Plant added to favorites.")
    return redirect(url_for('view_favorites'))

@app.route('/plant_care_guides', methods=['GET'])
# @login_required
def plant_care():
    plant_id = request.args.get("plant_id")  # Retrieve plant_id from query params
    if not plant_id:
        flash("Plant ID is required.", "error")
        return redirect(url_for('plant_care_guides'))  # Redirect if plant_id is missing
    
    # API URL for fetching plant care guides
    api_url = f"https://perenual.com/api/species-care-guide/{plant_id}?key={config.Config.API_KEY}"
    
    response = requests.get(api_url)
    if response.status_code == 200:
            plant_care_guide = response.json()  # Parse the JSON response
            return render_template('plant_care.html', plant_care_guide=plant_care_guide)  # Pass data to template


@app.route('/plant_diseases', methods=['GET'])
def view_diseases():
    api_url = f"https://perenual.com/api/pest-disease-list?key={config.Config.API_KEY}"
    response = requests.get(api_url)
    if response.status_code == 200:
        diseases = response.json().get('data', [])  # Extract data from the response
        print(diseases)  # Print the data for inspection
        return render_template('plant_diseases.html', diseases=diseases)
    else:
        return "Failed to fetch plant diseases", 500

@app.route('/plants')
def show_plants():
    # API URL to fetch plant data
    api_url = f"https://perenual.com/api/species-list?key={config.Config.API_KEY}"

    response = requests.get(api_url)
    if response.status_code == 200:
        # Extract plant data from the response
        plant_data = response.json().get("data", [])

        # Optionally, extract image URLs from the data
        plants_with_images = []
        for plant in plant_data:
            plant_info = {
                "name": plant.get("common_name", "Unknown Plant"),
                "scientific_name": plant.get("scientific_name", "Unknown"),
                "image_url": plant.get("image", {}).get("url", None)  # Adjust based on your API response structure
            }
            plants_with_images.append(plant_info)

        return render_template('plants.html', plants=plants_with_images)  # Pass data with images to the template

    flash('Failed to retrieve plant data.', 'error')
    return redirect(url_for('index'))