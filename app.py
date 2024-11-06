import os
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

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

with app.app_context():
    import models
    db.create_all()

@app.route('/')
def inventory():
    beverages = models.Beverage.query.all()
    return render_template('inventory.html', beverages=beverages)

@app.route('/restock')
def restock():
    beverages = models.Beverage.query.all()
    return render_template('restock.html', beverages=beverages)

@app.route('/statistics')
def statistics():
    beverages = models.Beverage.query.all()
    return render_template('statistics.html', beverages=beverages)

@app.route('/api/decrease/<int:beverage_id>', methods=['POST'])
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
    return jsonify({'success': False, 'error': 'Out of stock'}), 400

@app.route('/api/restock', methods=['POST'])
def add_restock():
    name = request.form.get('name')
    quantity = int(request.form.get('quantity', 0))
    price = float(request.form.get('price', 0))
    
    beverage = models.Beverage.query.filter_by(name=name).first()
    if not beverage:
        beverage = models.Beverage(name=name, quantity=0, price=price)
        db.session.add(beverage)
    
    beverage.quantity += quantity
    transaction = models.Transaction(
        beverage_id=beverage.id,
        quantity_change=quantity,
        transaction_type='restock'
    )
    db.session.add(transaction)
    db.session.commit()
    
    flash('Inventory updated successfully!', 'success')
    return redirect(url_for('restock'))

@app.route('/api/stats')
def get_stats():
    # Get sales data for the last 30 days
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
