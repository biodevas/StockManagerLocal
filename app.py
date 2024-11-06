import os
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

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

db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'

with app.app_context():
    import models
    db.create_all()

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
        
        beverage.quantity += quantity
        
        # Create transaction after beverage is committed
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
