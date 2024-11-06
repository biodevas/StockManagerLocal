from datetime import datetime
from app import db

class Beverage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beverage_id = db.Column(db.Integer, db.ForeignKey('beverage.id'), nullable=False)
    quantity_change = db.Column(db.Integer, nullable=False)  # negative for sales, positive for restocks
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'sale' or 'restock'
