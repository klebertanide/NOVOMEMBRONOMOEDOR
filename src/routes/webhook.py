from flask import Blueprint, request, jsonify
from src.models.user import db, Member, Affiliate, Sale
from datetime import datetime
import json
import requests

webhook_bp = Blueprint('webhook', __name__)

# ID do produto MOEDOR
MOEDOR_PRODUCT_ID = "R97937595F"

def send_realtime_notification(member_data):
    """Envia notificação em tempo real via SSE para novo membro"""
    try:
        notification_data = {
            'type': 'new_member',
            'data': member_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Envia para o endpoint de broadcast SSE
        requests.post(
            'http://localhost:5000/sse/broadcast',
            json=notification_data,
            timeout=1
        )
    except Exception as e:
        print(f"Erro ao enviar notificação em tempo real: {e}")

@webhook_bp.route('/hotmart', methods=['POST'])
def hotmart_webhook():
    """
    Endpoint para receber webhooks da Hotmart - MOEDOR
    """
    try:
        # Recebe os dados do webhook
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # Verifica se é um evento de compra aprovada
        if data.get('event') != 'PURCHASE_APPROVED':
            return jsonify({'message': 'Event not processed'}), 200
        
        # Extrai informações da venda
        purchase_data = data.get('data', {})
        purchase_info = purchase_data.get('purchase', {})
        buyer_info = purchase_data.get('buyer', {})
        product_info = purchase_data.get('product', {})
        
        # Verifica se é uma compra do produto MOEDOR
        product_id = str(product_info.get('id', ''))
        if product_id != MOEDOR_PRODUCT_ID:
            return jsonify({'message': 'Product not monitored'}), 200
        
        # Extrai informações do comprador
        buyer_name = buyer_info.get('name', '')
        buyer_email = buyer_info.get('email', '')
        transaction_id = purchase_info.get('transaction', '')
        
        if not buyer_name or not buyer_email or not transaction_id:
            return jsonify({'error': 'Missing required buyer information'}), 400
        
        # Verifica se já existe um membro com este transaction_id
        existing_member = Member.query.filter_by(transaction_id=transaction_id).first()
        if existing_member:
            return jsonify({'message': 'Member already exists'}), 200
        
        # Cria novo membro do MOEDOR
        new_member = Member(
            name=buyer_name,
            email=buyer_email,
            transaction_id=transaction_id,
            product_id=product_id,
            price=purchase_info.get('price', {}).get('value', 0),
            currency=purchase_info.get('price', {}).get('currency_value', 'USD'),
            is_new=True
        )
        
        db.session.add(new_member)
        db.session.commit()
        
        # Envia notificação em tempo real
        send_realtime_notification({
            'id': new_member.id,
            'name': buyer_name,
            'email': buyer_email,
            'transaction_id': transaction_id,
            'join_date': new_member.join_date.isoformat(),
            'price': new_member.price,
            'currency': new_member.currency
        })
        
        print(f"🎉 NOVO MEMBRO NO MOEDOR: {buyer_name}")
        
        return jsonify({
            'message': 'New MOEDOR member added successfully',
            'member_info': {
                'name': buyer_name,
                'email': buyer_email,
                'transaction_id': transaction_id
            }
        }), 200
        
    except Exception as e:
        print(f"Erro ao processar webhook: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@webhook_bp.route('/test', methods=['POST'])
def test_webhook():
    """
    Endpoint para testar o sistema com dados simulados do MOEDOR
    """
    try:
        # Gera nome aleatório para teste
        test_names = [
            "João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", 
            "Carlos Ferreira", "Lucia Almeida", "Rafael Souza", "Camila Lima"
        ]
        import random
        test_name = random.choice(test_names)
        
        # Dados de teste simulando um webhook da Hotmart para o MOEDOR
        test_data = {
            "event": "PURCHASE_APPROVED",
            "data": {
                "purchase": {
                    "transaction": f"TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "price": {
                        "value": 5.0,
                        "currency_value": "USD"
                    }
                },
                "buyer": {
                    "name": test_name,
                    "email": f"{test_name.lower().replace(' ', '.')}@email.com"
                },
                "product": {
                    "id": MOEDOR_PRODUCT_ID,
                    "name": "MOEDOR"
                }
            }
        }
        
        # Processa os dados de teste usando a mesma lógica do webhook real
        return hotmart_webhook_logic(test_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def hotmart_webhook_logic(data):
    """
    Lógica principal do webhook extraída para reutilização
    """
    # Extrai informações da venda
    purchase_data = data.get('data', {})
    purchase_info = purchase_data.get('purchase', {})
    buyer_info = purchase_data.get('buyer', {})
    product_info = purchase_data.get('product', {})
    
    # Verifica se é uma compra do produto MOEDOR
    product_id = str(product_info.get('id', ''))
    if product_id != MOEDOR_PRODUCT_ID:
        return jsonify({'message': 'Product not monitored'}), 200
    
    # Extrai informações do comprador
    buyer_name = buyer_info.get('name', '')
    buyer_email = buyer_info.get('email', '')
    transaction_id = purchase_info.get('transaction', '')
    
    if not buyer_name or not buyer_email or not transaction_id:
        return jsonify({'error': 'Missing required buyer information'}), 400
    
    # Verifica se já existe um membro com este transaction_id
    existing_member = Member.query.filter_by(transaction_id=transaction_id).first()
    if existing_member:
        return jsonify({'message': 'Member already exists'}), 200
    
    # Cria novo membro do MOEDOR
    new_member = Member(
        name=buyer_name,
        email=buyer_email,
        transaction_id=transaction_id,
        product_id=product_id,
        price=purchase_info.get('price', {}).get('value', 0),
        currency=purchase_info.get('price', {}).get('currency_value', 'USD'),
        is_new=True
    )
    
    db.session.add(new_member)
    db.session.commit()
    
    # Envia notificação em tempo real
    send_realtime_notification({
        'id': new_member.id,
        'name': buyer_name,
        'email': buyer_email,
        'transaction_id': transaction_id,
        'join_date': new_member.join_date.isoformat(),
        'price': new_member.price,
        'currency': new_member.currency
    })
    
    print(f"🎉 NOVO MEMBRO NO MOEDOR: {buyer_name}")
    
    return jsonify({
        'message': 'New MOEDOR member added successfully',
        'member_info': {
            'name': buyer_name,
            'email': buyer_email,
            'transaction_id': transaction_id
        }
    }), 200

