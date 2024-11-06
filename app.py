import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# File Upload Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_IMAGE_SIZE = (800, 800)
DEFAULT_IMAGE = 'default_beverage.png'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Set directory permissions
os.chmod(UPLOAD_FOLDER, 0o755)

db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'

with app.app_context():
    import models
    db.drop_all()  # Drop all tables
    db.create_all()  # Recreate all tables

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_path):
    try:
        with Image.open(image_path) as img:
            img.thumbnail(MAX_IMAGE_SIZE)
            img.save(image_path, optimize=True, quality=85)
        logger.info(f"Image processed successfully: {image_path}")
        return True
    except Exception as e:
        logger.error(f"Error processing image {image_path}: {str(e)}")
        return False

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = models.User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('inventory'))
        flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if models.User.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'danger')
            return redirect(url_for('register'))
        
        user = models.User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registro exitoso. Por favor inicie sesión', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def inventory():
    beverages = models.Beverage.query.all()
    for beverage in beverages:
        if beverage.image_path:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], beverage.image_path)
            logger.debug(f"Image path for {beverage.name}: {image_path}")
            if not os.path.exists(image_path):
                logger.warning(f"Image not found for {beverage.name}: {image_path}")
                beverage.image_path = DEFAULT_IMAGE
    return render_template('inventory.html', beverages=beverages)

@app.route('/restock')
@login_required
def restock():
    beverages = models.Beverage.query.all()
    return render_template('restock.html', beverages=beverages)

@app.route('/statistics')
@login_required
def statistics():
    beverages = models.Beverage.query.all()
    return render_template('statistics.html', beverages=beverages)

@app.route('/api/decrease/<int:beverage_id>', methods=['POST'])
@login_required
def decrease_inventory(beverage_id):
    beverage = models.Beverage.query.get_or_404(beverage_id)
    if beverage.quantity > 0:
        beverage.quantity -= 1
        transaction = models.Transaction(
            beverage_id=beverage_id,
            quantity_change=-1,
            transaction_type='sale'
        )
        db.session.add(transaction)
        db.session.commit()
        return jsonify({'success': True, 'new_quantity': beverage.quantity})
    return jsonify({'success': False, 'error': 'Sin existencias'}), 400

@app.route('/api/restock', methods=['POST'])
@login_required
def add_restock():
    try:
        name = request.form.get('name')
        quantity = int(request.form.get('quantity', 0))
        price = float(request.form.get('price', 0))
        
        if not name or quantity <= 0 or price <= 0:
            flash('Por favor complete todos los campos correctamente', 'danger')
            return redirect(url_for('restock'))
        
        beverage = models.Beverage.query.filter_by(name=name).first()
        if not beverage:
            beverage = models.Beverage(name=name, quantity=0, price=price)
            db.session.add(beverage)
            db.session.commit()  # Commit to get the beverage.id
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                try:
                    filename = secure_filename(f"{beverage.id}_{file.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    if process_image(filepath):
                        beverage.image_path = filename
                        logger.info(f"Image uploaded successfully for {beverage.name}: {filepath}")
                    else:
                        beverage.image_path = DEFAULT_IMAGE
                        logger.error(f"Failed to process image for {beverage.name}")
                except Exception as e:
                    logger.error(f"Error saving image for {beverage.name}: {str(e)}")
                    beverage.image_path = DEFAULT_IMAGE
            else:
                logger.warning(f"Invalid or no image file provided for {beverage.name}")
                beverage.image_path = DEFAULT_IMAGE
        else:
            beverage.image_path = DEFAULT_IMAGE
        
        beverage.quantity += quantity
        
        transaction = models.Transaction(
            beverage_id=beverage.id,
            quantity_change=quantity,
            transaction_type='restock'
        )
        db.session.add(transaction)
        db.session.commit()
        
        flash('¡Inventario actualizado exitosamente!', 'success')
        return redirect(url_for('restock'))
    except Exception as e:
        logger.error(f"Error in add_restock: {str(e)}")
        db.session.rollback()
        flash('Error al actualizar el inventario: ' + str(e), 'danger')
        return redirect(url_for('restock'))

@app.route('/api/stats')
@login_required
def get_stats():
    beverages = models.Beverage.query.all()
    stats = []
    for beverage in beverages:
        sales = models.Transaction.query.filter_by(
            beverage_id=beverage.id,
            transaction_type='sale'
        ).count()
        stats.append({
            'name': beverage.name,
            'sales': abs(sales)
        })
    return jsonify(stats)
