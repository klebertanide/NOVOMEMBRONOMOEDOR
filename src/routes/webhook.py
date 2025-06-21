from flask import Blueprint, request, jsonify
from src.models.user import db, Member, Sale
from datetime import datetime
import json
import requests

webhook_bp = Blueprint('webhook', __name__)

def send_sse_notification(data):
    """Envia notificação via SSE para clientes conectados"""
    try:
        # Envia para endpoint SSE local
        requests.post(f'http://localhost:5000/api/notify', 
                     json=data, 
                     timeout=1)
    except:
        pass  # Falha silenciosa se SSE não estiver disponível

@webhook_bp.route('/hotmart', methods=['POST'])
def hotmart_webhook():
    """Recebe webhooks da Hotmart para vendas do MOEDOR"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # Log para debug
        print(f"📨 Webhook recebido: {json.dumps(data, indent=2)}")
        
        # Verifica se é uma venda aprovada
        event_type = data.get('event')
        if event_type != 'PURCHASE_APPROVED':
            return jsonify({'message': 'Event type not handled'}), 200
        
        # Extrai dados da venda
        purchase_data = data.get('data', {})
        product = purchase_data.get('product', {})
        buyer = purchase_data.get('buyer', {})
        
        # Verifica se é o produto MOEDOR (ID: R97937595F)
        product_id = product.get('id')
        if product_id != 'R97937595F':
            print(f"❌ Produto não é MOEDOR: {product_id}")
            return jsonify({'message': 'Product not MOEDOR'}), 200
        
        # Extrai informações do comprador
        buyer_name = buyer.get('name', 'Membro Anônimo')
        buyer_email = buyer.get('email', '')
        
        # Verifica se já existe este membro
        existing_member = Member.query.filter_by(email=buyer_email).first()
        
        if not existing_member:
            # Cria novo membro
            new_member = Member(
                name=buyer_name,
                email=buyer_email,
                code=f"MOEDOR{datetime.now().strftime('%Y%m%d%H%M%S')}",
                join_date=datetime.utcnow(),
                product_id='R97937595F'
            )
            
            db.session.add(new_member)
            
            # Cria registro de venda
            new_sale = Sale(
                member_id=new_member.id,
                product_id='R97937595F',
                amount=5.00,  # Preço do MOEDOR
                currency='USD',
                sale_date=datetime.utcnow(),
                transaction_id=purchase_data.get('transaction', '')
            )
            
            db.session.add(new_sale)
            db.session.commit()
            
            print(f"🎉 NOVO MEMBRO NO MOEDOR: {buyer_name} ({new_member.code})")
            
            # Envia notificação SSE
            send_sse_notification({
                'type': 'new_member',
                'data': {
                    'id': new_member.id,
                    'name': new_member.name,
                    'code': new_member.code,
                    'join_date': new_member.join_date.isoformat()
                }
            })
            
            return jsonify({
                'message': 'New MOEDOR member created',
                'member': {
                    'name': new_member.name,
                    'code': new_member.code
                }
            }), 201
        else:
            print(f"✅ Membro já existe: {buyer_name}")
            return jsonify({'message': 'Member already exists'}), 200
            
    except Exception as e:
        print(f"❌ Erro no webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

@webhook_bp.route('/test', methods=['POST'])
def test_webhook():
    """Endpoint para testar notificações"""
    try:
        # Cria membro de teste
        test_member = Member(
            name='Membro Teste',
            email=f'teste{datetime.now().strftime("%H%M%S")}@moedor.com',
            code=f'TEST{datetime.now().strftime("%Y%m%d%H%M%S")}',
            join_date=datetime.utcnow(),
            product_id='R97937595F'
        )
        
        db.session.add(test_member)
        
        # Cria venda de teste
        test_sale = Sale(
            member_id=test_member.id,
            product_id='R97937595F',
            amount=5.00,
            currency='USD',
            sale_date=datetime.utcnow(),
            transaction_id=f'TEST_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        )
        
        db.session.add(test_sale)
        db.session.commit()
        
        print(f"🎉 TESTE - NOVO MEMBRO NO MOEDOR: {test_member.name} ({test_member.code})")
        
        # Envia notificação SSE
        send_sse_notification({
            'type': 'new_member',
            'data': {
                'id': test_member.id,
                'name': test_member.name,
                'code': test_member.code,
                'join_date': test_member.join_date.isoformat()
            }
        })
        
        return jsonify({
            'message': 'Test member created successfully',
            'member': {
                'name': test_member.name,
                'code': test_member.code
            }
        }), 201
        
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        return jsonify({'error': str(e)}), 500

@webhook_bp.route('/health', methods=['GET'])
def health_check():
    """Health check para o webhook"""
    return jsonify({
        'status': 'healthy',
        'service': 'MOEDOR Webhook',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

