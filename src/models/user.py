from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class Member(db.Model):
    """Modelo para membros do MOEDOR"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    product_id = db.Column(db.String(50), nullable=False)  # R97937595F para MOEDOR
    join_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    price = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), nullable=True, default='USD')
    is_new = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Member {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'transaction_id': self.transaction_id,
            'product_id': self.product_id,
            'join_date': self.join_date.isoformat(),
            'price': self.price,
            'currency': self.currency,
            'is_new': self.is_new
        }

class Sale(db.Model):
    """Modelo para vendas do MOEDOR"""
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    product_id = db.Column(db.String(50), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    buyer_name = db.Column(db.String(200), nullable=False)
    buyer_email = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False, default='USD')
    sale_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default='APPROVED')
    
    def __repr__(self):
        return f'<Sale {self.transaction_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'buyer_name': self.buyer_name,
            'buyer_email': self.buyer_email,
            'price': self.price,
            'currency': self.currency,
            'sale_date': self.sale_date.isoformat(),
            'status': self.status
        }

# Modelo antigo mantido para compatibilidade
class Affiliate(db.Model):
    """Modelo antigo para afiliados (mantido para compatibilidade)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(200), nullable=True)
    join_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_new = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Affiliate {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'email': self.email,
            'join_date': self.join_date.isoformat(),
            'is_new': self.is_new
        }

