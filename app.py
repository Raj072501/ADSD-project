from flask import Flask, render_template, request, redirect, url_for, flash, g
import sqlite3
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import os
from bson.objectid import ObjectId
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FileField
from wtforms.validators import DataRequired

# Flask Application Initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Raj123'
app.config['UPLOAD_FOLDER'] = './static/images'

# Flask-Session Configuration
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_PERMANENT=True
)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login if not authenticated

# MongoDB connection
client = MongoClient("mongodb+srv://Rajesh:Raj123@cluster0.vh5yz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['classic_vehicles']
images_collection = db['vehicle_images']

# Function to get a database connection per request
def get_db():
    if 'sqlite_db' not in g:
        g.sqlite_db = sqlite3.connect('vehicles.db')
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('sqlite_db', None)
    if db is not None:
        db.close()

# User model
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(user[0], user[1], user[2])
    return None

def fetch_vehicles(filters=None):
    query = "SELECT * FROM vehicles WHERE 1=1"
    params = []

    valid_columns = ['name', 'category', 'make', 'model', 'year', 'engine_type', 'origin']

    if filters:
        for key, value in filters.items():
            if key in valid_columns:
                query += f" AND {key} LIKE ?"
                params.append(f"%{value}%")

    cursor = get_db().cursor()
    cursor.execute(query, params)
    return cursor.fetchall()

# Define the LoginForm class
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Define the DeleteForm class
class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')

# Define the AddVehicleForm class
class AddVehicleForm(FlaskForm):
    car_name = StringField('Car Name', validators=[DataRequired()])
    category = SelectField('Category', choices=['Car', 'Truck', 'Bike'])
    make = StringField('Make', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    engine_type = StringField('Engine Type', validators=[DataRequired()])
    origin = StringField('Origin', validators=[DataRequired()])
    image = FileField('Image', validators=[DataRequired()])

# Default route to redirect to login
@app.route('/')
def default_route():
    return redirect(url_for('login'))

@app.route('/index')
@login_required  # Require login to access the index page
def index():
    filters = request.args.to_dict()
    vehicles = fetch_vehicles(filters)
    delete_form = DeleteForm()  # Create delete form instance
    return render_template('index.html', vehicles=vehicles, delete_form=delete_form)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    form = AddVehicleForm()
    if form.validate_on_submit():
        try:
            car_name = form.car_name.data
            category = form.category.data
            make = form.make.data
            model = form.model.data
            year = form.year.data
            engine_type = form.engine_type.data
            origin = form.origin.data

            file = form.image.data
            if file:
                # Validate image type and size
                if file.content_type not in ['image/jpeg', 'image/png']:
                    flash('Invalid image type', 'danger')
                    return redirect(url_for('add_vehicle'))
                
                if file.content_length > 1024 * 1024:
                    flash('Image size exceeds 1MB', 'danger')
                    return redirect(url_for('add_vehicle'))
                
                # Save the file to the static/images folder
                filename = secure_filename(file.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(upload_path)

                # Save the relative path to the database
                relative_path = f'images/{filename}'

                # Insert the vehicle data into the database
                cursor = get_db().cursor()
                cursor.execute(
                    "INSERT INTO vehicles (car_name, category, make, model, year, engine_type, origin, image_file_path) VALUES (?,?,?,?,?,?,?,?)",
                    (car_name, category, make, model, year, engine_type, origin, relative_path)
                )
                get_db().commit()
                flash('Vehicle added successfully!', 'success')
                return redirect(url_for('index'))
        except Exception as e:
            # Log the error
            app.logger.error(f'Error adding vehicle: {str(e)}')
            flash('An error occurred while adding the vehicle', 'danger')
    return render_template('add_vehicle.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Ensure this is creating a form object
    print("Login route accessed")  # To confirm the route is being hit
    if form.validate_on_submit():  # Check if form submission is valid
        username = form.username.data
        password = form.password.data
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user[2], password):
            login_user(User(user[0], user[1], user[2]))
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/delete/<int:vehicle_id>', methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    try:
        cursor = get_db().cursor()
        cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
        get_db().commit()
        flash('Vehicle deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting vehicle: {str(e)}', 'danger')
    return redirect(url_for('index'))

@app.route('/vehicle/<vehicle_id>', methods=['GET'])
@login_required
def view_vehicle(vehicle_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,))
    vehicle = cursor.fetchone()

    if vehicle:
        vehicle_dict = {
            'make': vehicle['make'],
            'model': vehicle['model'],
            'year': vehicle['year'],
            'engine': vehicle['engine_type'],  # Retrieve engine details
            'origin': vehicle['origin']
        }

        image_file_path = vehicle['image_file_path']
        if image_file_path:
            vehicle_dict['image_url'] = url_for('static', filename=image_file_path)
        else:
            vehicle_dict['image_url'] = url_for('static', filename='default_image.jpg')

        return render_template('view_vehicle.html', vehicle=vehicle_dict)
    else:
        flash('Vehicle not found!', 'danger')
    return redirect(url_for('index'))

@app.route('/update/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def update_vehicle(vehicle_id):
    cursor = get_db().cursor()
    if request.method == 'POST':
        car_name = request.form['car_name']
        category = request.form['category']
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        engine_type = request.form['engine_type']
        origin = request.form['origin']

        cursor.execute("""
    UPDATE vehicles
    SET car_name = ?, category = ?, make = ?, model = ?, year = ?, engine_type = ?, origin = ? 
    WHERE id = ? 
""", (car_name, category, make, model, year, engine_type, origin, vehicle_id))
        get_db().commit()
        flash('Vehicle updated successfully!', 'success')
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,))
    vehicle = cursor.fetchone()
    if vehicle is None:
        flash('Vehicle not found!', 'danger')
        return redirect(url_for('index'))

    return render_template('update_vehicle.html', vehicle=vehicle)
if __name__ == '__main__':
    app.run(debug=True, port=3001)