from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import config
import requests
import psycopg2

# Create Flask app
app = Flask(__name__)
app.config.from_object(config.Config)

# Initialize database and other extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import models after initializing db to avoid circular imports
from models import User, Plant, FavoritePlant, PlantCare, PlantDisease

# Function to initialize or reinitialize the database
def init_db():
    with app.app_context():
        db.drop_all()  # WARNING: This will erase all data
        db.create_all()  # Creates tables based on model definitions

# Call this function when initializing the database
init_db()  # Comment out after initializing to avoid data loss

# Define user loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Ensure Flask-Login logs out the user
    session.clear()  # Clear session data
    # Redirect to the login page or another desired page after logging out
    return redirect(url_for('login'))
    


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
            # return redirect(url_for('profile', username=user.username)) 
            return redirect(url_for('profile', username=user.username))

        else:
            flash('Invalid username or password. Please try again.', 'error')
            return redirect(url_for('login'))  # Return with error message

    return render_template('login.html')  # Render login form for GET requests



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
def plant_care():
    plant_id = request.args.get("plant_id")

    if not plant_id or not plant_id.isdigit():
        flash("Invalid or missing Plant ID.", "error")
        return redirect(url_for('index'))  # Redirect to a safe page
    
    plant_id = int(plant_id)  # Convert to integer

    # Fetch the care guide from the API or database
    api_url = f"https://perenual.com/api/species-care-guide/{plant_id}?key={config.Config.API_KEY}"
    response = requests.get(api_url)

    if response.status_code == 200:
        plant_care_guide = response.json()
        return render_template('plant_care.html', plant_care_guide=plant_care_guide)
    else:
        flash("Could not fetch the plant care guide. Please try again.", "error")
        return redirect(url_for('index'))  # Redirect if the request fails
    

    @app.route('/plant_care/<int:plant_id>', methods=['GET'])
    def plant_care(plant_id):
    # API URL to fetch plant care guide based on plant_id
        api_url = f"https://perenual.com/api/species-care-guide/{plant_id}?key={API_KEY}"

    response = requests.get(api_url)
    if response.status_code == 200:
        plant_care_guide = response.json()  # Parse the JSON response
        return render_template('plant_care.html', plant_care_guide=plant_care_guide)  # Render with care guide
    else:
        flash("Failed to retrieve plant care guide.", "error")
        return redirect(url_for('show_plants'))  # Redirect to plant list on failure



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