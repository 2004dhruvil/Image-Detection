import os
import random
import time
from datetime import datetime
import cv2
import numpy as np
import joblib
from skimage.feature import hog
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
from flask import session

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- ML Model Loading ---
IMG_SIZE = 128
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'best_svm_model.pkl')
SCALER_PATH = os.path.join(os.path.dirname(__file__), 'scaler.pkl')

try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("[INFO] Model and Scaler loaded successfully!")
except Exception as e:
    print(f"[ERROR] Error loading model/scaler: {e}")
    model = None
    scaler = None

def preprocess_and_extract(img_path):
    try:
        img = cv2.imread(img_path)
        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # HOG feature extraction
        hog_features = hog(
            gray,
            orientations=9,
            pixels_per_cell=(8, 8),
            cells_per_block=(2, 2),
            block_norm='L2-Hys'
        )
        return hog_features
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return None

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
# Construct MySQL URI if details provided, otherwise fallback to SQLite
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME')

if DB_USER and DB_PASSWORD and DB_NAME:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize Extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    # Relationship to scan history
    scans = db.relationship('ScanHistory', backref='user', lazy=True)

class ScanHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    prediction_label = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def real_predict(filepath):
    """
    Real prediction function using the loaded SVM model.
    """
    if model is None or scaler is None:
        return {"label": "Error", "confidence": "0% (Model not loaded)"}
    
    features = preprocess_and_extract(filepath)
    if features is None:
        return {"label": "Error", "confidence": "0% (Processing failed)"}
    
    # Reshape and scale
    features = features.reshape(1, -1)
    features_scaled = scaler.transform(features)
    
    # Predict
    prediction = model.predict(features_scaled)
    # SVM decision_function or predict_proba can give a sense of "confidence"
    # but SVC by default doesn't provide proba unless trained with it.
    # We'll use a placeholder confidence or the distance from hyperplane if available.
    try:
        dist = model.decision_function(features_scaled)[0]
        # Map distance to a pseudo-confidence percentage
        confidence = 100 / (1 + np.exp(-abs(dist))) 
    except:
        confidence = 99.0 # Fallback
    
    label = "Fake" if prediction[0] == 1 else "Real"
    
    return {
        "label": label,
        "confidence": f"{confidence:.2f}%"
    }

# Routes
@app.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user)

@app.route('/history')
@login_required
def history():
    # Fetch user's scan history
    history = ScanHistory.query.filter_by(user_id=current_user.id).order_by(ScanHistory.timestamp.desc()).all()
    total_scans = len(history)
    return render_template('history.html', user=current_user, history=history, total_scans=total_scans)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_captcha = request.form.get('captcha')
        not_robot = request.form.get('not_robot')
        
        # Verify "I am not a robot" checkbox
        if not not_robot:
            flash('Please verify that you are not a robot.', 'danger')
            return redirect(url_for('login'))
        
        # Verify Math CAPTCHA first
        if not user_captcha or 'captcha_answer' not in session or int(user_captcha) != session['captcha_answer']:
            flash('Incorrect CAPTCHA answer. Please try again.', 'danger')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            if user.is_admin:
                 flash('Please use the admin login page for admin accounts.', 'warning')
                 return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            
    # Generate new CAPTCHA for GET request or failed login
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    session['captcha_answer'] = num1 + num2
    
    return render_template('login.html', num1=num1, num2=num2)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            if not user.is_admin:
                flash('Access denied. Admin only.', 'danger')
                return redirect(url_for('admin_login'))
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Admin Login Unsuccessful.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    
    # Calculate Admin Analytics
    total_users = User.query.count()
    total_scans = ScanHistory.query.count()
    fake_scans = ScanHistory.query.filter_by(prediction_label='Fake').count()
    real_scans = ScanHistory.query.filter_by(prediction_label='Real').count()
    
    # Fetch recent scans to show user activity
    recent_scans = ScanHistory.query.order_by(ScanHistory.timestamp.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html', 
                           users=users, 
                           user=current_user,
                           total_users=total_users,
                           total_scans=total_scans,
                           fake_scans=fake_scans,
                           real_scans=real_scans,
                           recent_scans=recent_scans)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Username already exists.', 'warning')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, is_admin=False)
        
        # Determine if this is the first user (make them admin for setup simplicity)
        if User.query.count() == 0:
            new_user.is_admin = True
            flash('First user created as Admin!', 'success')
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created! You can now login.', 'success')
        flash('Account created! You can now login.', 'success')
        if new_user.is_admin:
             return redirect(url_for('admin_login'))
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Run prediction
        result = real_predict(filepath)
        
        # Clean up uploaded file (optional, keeping it simple for now)
        # os.remove(filepath) 
        
        # Save to history
        new_scan = ScanHistory(
            user_id=current_user.id,
            filename=filename,
            prediction_label=result['label'],
            confidence=result['confidence']
        )
        db.session.add(new_scan)
        db.session.commit()
        
        return jsonify(result)
    
    return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
