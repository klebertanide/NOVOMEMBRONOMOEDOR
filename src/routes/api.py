from flask import Blueprint, jsonify, request
from src.models.user import db, Affiliate, Sale
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__)

@api_bp.route('/new-affiliates', methods=['GET'])
def get_new_affiliates():
    """
    Retorna afiliados que ainda não foram exibidos como novos
    """
    try:
        new_affiliates = Affiliate.query.filter_by(is_new=True).all()
        
        affiliates_data = []
        for affiliate in new_affiliates:
            affiliates_data.append({
                'id': affiliate.id,
                'name': affiliate.name,
                'code': affiliate.affiliate_code,
                'first_sale_date': affiliate.first_sale_date.isoformat(),
                'total_sales': affiliate.total_sales
            })
        
        return jsonify({
            'new_affiliates': affiliates_data,
            'count': len(affiliates_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/mark-affiliate-shown/<int:affiliate_id>', methods=['POST'])
def mark_affiliate_shown(affiliate_id):
    """
    Marca um afiliado como já exibido (não é mais novo)
    """
    try:
        affiliate = Affiliate.query.get(affiliate_id)
        if not affiliate:
            return jsonify({'error': 'Affiliate not found'}), 404
        
        affiliate.is_new = False
        db.session.commit()
        
        return jsonify({'message': 'Affiliate marked as shown'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/affiliates', methods=['GET'])
def get_all_affiliates():
    """
    Retorna todos os afiliados cadastrados
    """
    try:
        affiliates = Affiliate.query.order_by(Affiliate.first_sale_date.desc()).all()
        
        affiliates_data = []
        for affiliate in affiliates:
            affiliates_data.append(affiliate.to_dict())
        
        return jsonify({
            'affiliates': affiliates_data,
            'total': len(affiliates_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sales', methods=['GET'])
def get_recent_sales():
    """
    Retorna vendas recentes (últimas 24 horas por padrão)
    """
    try:
        # Pega parâmetro de horas (padrão 24)
        hours = request.args.get('hours', 24, type=int)
        since = datetime.utcnow() - timedelta(hours=hours)
        
        sales = Sale.query.filter(Sale.sale_date >= since).order_by(Sale.sale_date.desc()).all()
        
        sales_data = []
        for sale in sales:
            sales_data.append(sale.to_dict())
        
        return jsonify({
            'sales': sales_data,
            'total': len(sales_data),
            'period_hours': hours
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Retorna estatísticas gerais do sistema
    """
    try:
        total_affiliates = Affiliate.query.count()
        new_affiliates_count = Affiliate.query.filter_by(is_new=True).count()
        total_sales = Sale.query.count()
        
        # Vendas das últimas 24 horas
        since_24h = datetime.utcnow() - timedelta(hours=24)
        sales_24h = Sale.query.filter(Sale.sale_date >= since_24h).count()
        
        # Novos afiliados das últimas 24 horas
        new_affiliates_24h = Affiliate.query.filter(Affiliate.first_sale_date >= since_24h).count()
        
        return jsonify({
            'total_affiliates': total_affiliates,
            'new_affiliates_pending': new_affiliates_count,
            'total_sales': total_sales,
            'sales_last_24h': sales_24h,
            'new_affiliates_last_24h': new_affiliates_24h
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/reset-new-flags', methods=['POST'])
def reset_new_flags():
    """
    Marca todos os afiliados como já exibidos (para testes)
    """
    try:
        Affiliate.query.update({'is_new': False})
        db.session.commit()
        
        return jsonify({'message': 'All affiliates marked as shown'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

