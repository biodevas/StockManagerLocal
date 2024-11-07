import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_from_directory, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timedelta
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image
import PIL.WebPImagePlugin  # Explicit WebP support
import imghdr
import csv
import io
from dotenv import load_dotenv
from email_service import send_low_stock_alert

load_dotenv()  # This will load the environment variables from .env file

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Please ensure all required environment variables are properly configured."
    )
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'avif'}
MAX_IMAGE_SIZE = (800, 800)
MAX_FILE_SIZE = 5 * 1024 * 1024
DEFAULT_IMAGE = 'default_beverage.png'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.chmod(UPLOAD_FOLDER, 0o755)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'

with app.app_context():
    import models
    db.create_all()

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_path):
    try:
        with Image.open(image_path) as img:
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, 'white')
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])
                else:
                    background.paste(img, mask=img.split()[1])
                img = background

            if img.size[0] > MAX_IMAGE_SIZE[0] or img.size[1] > MAX_IMAGE_SIZE[1]:
                img.thumbnail(MAX_IMAGE_SIZE)

            format = img.format if img.format else 'JPEG'
            save_options = {}
            
            if format == 'JPEG':
                save_options = {'quality': 85, 'optimize': True}
            elif format == 'PNG':
                save_options = {'optimize': True}
            elif format == 'WEBP':
                save_options = {'quality': 85, 'method': 6}
            
            img.save(image_path, format=format, **save_options)
            os.chmod(image_path, 0o644)
            logger.info(f"Image processed successfully: {image_path}")
            return True
            
    except Exception as e:
        logger.error(f"Error processing image {image_path}: {str(e)}")
        if os.path.exists(image_path):
            os.remove(image_path)
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
                db.session.commit()
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
            user_id=current_user.id,
            quantity_change=-1,
            transaction_type='sale'
        )
        db.session.add(transaction)
        db.session.commit()
        
        # Check if stock is low and send alert
        if beverage.quantity < 5:
            send_low_stock_alert(
                beverage_name=beverage.name,
                current_quantity=beverage.quantity,
                user_email=current_user.email
            )
        
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
            beverage = models.Beverage(name=name, quantity=0, price=price, image_path=DEFAULT_IMAGE)
            db.session.add(beverage)
            db.session.commit()
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                try:
                    if not allowed_file(file.filename):
                        raise ValueError("El formato de archivo no está permitido. Formatos permitidos: " + 
                                      ", ".join(ALLOWED_EXTENSIONS))
                    
                    file_ext = validate_image(file.stream)
                    if not file_ext and not file.filename.lower().endswith('.webp'):
                        raise ValueError("El formato de imagen no es válido")
                    
                    if file.filename.lower().endswith('.webp'):
                        file_ext = '.webp'
                    filename = secure_filename(f"{beverage.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    
                    logger.debug(f"Saving image for {beverage.name} to {filepath}")
                    file.save(filepath)
                    
                    if process_image(filepath):
                        if beverage.image_path and beverage.image_path != DEFAULT_IMAGE:
                            old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], beverage.image_path)
                            if os.path.exists(old_image_path):
                                os.remove(old_image_path)
                                logger.info(f"Removed old image: {old_image_path}")
                        
                        beverage.image_path = filename
                        logger.info(f"Image uploaded successfully for {beverage.name}: {filepath}")
                    else:
                        raise ValueError("Error al procesar la imagen. Por favor, intente con otra imagen")
                except ValueError as ve:
                    logger.error(f"Validation error for {beverage.name}: {str(ve)}")
                    flash(str(ve), 'danger')
                    if not beverage.image_path:
                        beverage.image_path = DEFAULT_IMAGE
                except Exception as e:
                    logger.error(f"Error saving image for {beverage.name}: {str(e)}")
                    flash('Error al subir la imagen. Por favor, intente nuevamente', 'danger')
                    if not beverage.image_path:
                        beverage.image_path = DEFAULT_IMAGE
        
        beverage.quantity += quantity
        
        transaction = models.Transaction(
            beverage_id=beverage.id,
            user_id=current_user.id,
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
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = datetime.now() - timedelta(days=30)
            
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date + timedelta(days=1)
        else:
            end_date = datetime.now()
        
        sales_query = db.session.query(
            models.Transaction.beverage_id,
            models.Beverage.name,
            models.User.email.label('user_email'),
            db.func.sum(db.func.abs(models.Transaction.quantity_change)).label('total_sales')
        ).join(
            models.Beverage
        ).join(
            models.User
        ).filter(
            models.Transaction.transaction_type == 'sale',
            models.Transaction.timestamp >= start_date,
            models.Transaction.timestamp <= end_date
        ).group_by(
            models.Transaction.beverage_id,
            models.Beverage.name,
            models.User.email
        )
        
        sales_data = []
        total_sales = 0
        top_product = None
        max_sales = 0
        
        for sale in sales_query.all():
            sales_count = int(sale.total_sales)
            sales_data.append({
                'name': sale.name,
                'user': sale.user_email,
                'sales': sales_count
            })
            total_sales += sales_count
            
            if sales_count > max_sales:
                max_sales = sales_count
                top_product = sale.name
        
        return jsonify({
            'sales_data': sales_data,
            'total_sales': total_sales,
            'top_product': top_product
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/sales')
@login_required
def export_sales():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = datetime.now() - timedelta(days=30)
            
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date + timedelta(days=1)
        else:
            end_date = datetime.now()

        sales = db.session.query(
            models.Beverage.name,
            models.Transaction.quantity_change,
            models.Transaction.timestamp,
            models.Beverage.price,
            models.User.email.label('user_email')
        ).join(
            models.Beverage
        ).join(
            models.User
        ).filter(
            models.Transaction.transaction_type == 'sale',
            models.Transaction.timestamp >= start_date,
            models.Transaction.timestamp <= end_date
        ).order_by(models.Transaction.timestamp.desc()).all()

        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerow(['Producto', 'Cantidad', 'Usuario', 'Fecha', 'Precio Unitario', 'Total'])

        for sale in sales:
            writer.writerow([
                sale.name,
                abs(sale.quantity_change),
                sale.user_email,
                sale.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                f"${sale.price:.2f}",
                f"${abs(sale.quantity_change * sale.price):.2f}"
            ])

        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename=ventas_{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    except Exception as e:
        logger.error(f"Error exporting sales: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/transactions')
@login_required
def export_transactions():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = datetime.now() - timedelta(days=30)
            
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date + timedelta(days=1)
        else:
            end_date = datetime.now()

        transactions = db.session.query(
            models.Beverage.name,
            models.Transaction.quantity_change,
            models.Transaction.timestamp,
            models.Transaction.transaction_type,
            models.User.email.label('user_email')
        ).join(
            models.Beverage
        ).join(
            models.User
        ).filter(
            models.Transaction.timestamp >= start_date,
            models.Transaction.timestamp <= end_date
        ).order_by(models.Transaction.timestamp.desc()).all()

        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerow(['Producto', 'Cantidad', 'Usuario', 'Tipo', 'Fecha'])

        for transaction in transactions:
            writer.writerow([
                transaction.name,
                abs(transaction.quantity_change),
                transaction.user_email,
                'Venta' if transaction.transaction_type == 'sale' else 'Reabastecimiento',
                transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ])

        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename=transacciones_{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    except Exception as e:
        logger.error(f"Error exporting transactions: {str(e)}")
        return jsonify({'error': str(e)}), 500