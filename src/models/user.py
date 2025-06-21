from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

class Member(db.Model):
    """Modelo para membros do MOEDOR (compradores/assinantes)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    product_id = db.Column(db.String(50), nullable=False)  # R97937595F
    join_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    price = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), nullable=True)
    is_new = db.Column(db.Boolean, default=True)  # Para controlar se já foi exibido como novo
    
    def __repr__(self):
        return f'<Member {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'transaction_id': self.transaction_id,
            'product_id': self.product_id,
            'join_date': self.join_date.isoformat() if self.join_date else None,
            'price': self.price,
            'currency': self.currency,
            'is_new': self.is_new
        }

# Manter modelos antigos para compatibilidade
class Affiliate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    affiliate_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    first_sale_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_sales = db.Column(db.Integer, default=1)
    is_new = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Affiliate {self.name} ({self.affiliate_code})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'affiliate_code': self.affiliate_code,
            'name': self.name,
            'first_sale_date': self.first_sale_date.isoformat() if self.first_sale_date else None,
            'total_sales': self.total_sales,
            'is_new': self.is_new
        }

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    affiliate_id = db.Column(db.Integer, db.ForeignKey('affiliate.id'), nullable=True)
    buyer_name = db.Column(db.String(200), nullable=False)
    buyer_email = db.Column(db.String(200), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    price = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), nullable=True)
    
    affiliate = db.relationship('Affiliate', backref=db.backref('sales', lazy=True))
    
    def __repr__(self):
        return f'<Sale {self.transaction_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'affiliate_id': self.affiliate_id,
            'buyer_name': self.buyer_name,
            'buyer_email': self.buyer_email,
            'product_name': self.product_name,
            'product_id': self.product_id,
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
            'price': self.price,
            'currency': self.currency,
            'affiliate': self.affiliate.to_dict() if self.affiliate else None
        }

