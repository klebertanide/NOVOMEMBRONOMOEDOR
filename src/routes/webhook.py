from flask import Blueprint, request, jsonify
from src.models.user import db, Affiliate, Sale
from datetime import datetime
import json
import requests

webhook_bp = Blueprint('webhook', __name__)

def send_realtime_notification(affiliate_data):
    """Envia notificação em tempo real via SSE"""
    try:
        notification_data = {
            'type': 'new_affiliate',
            'data': affiliate_data,
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
    Endpoint para receber webhooks da Hotmart
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
        affiliates_info = purchase_data.get('affiliates', [])
        
        # Cria registro da venda
        sale = Sale(
            transaction_id=purchase_info.get('transaction', ''),
            buyer_name=buyer_info.get('name', ''),
            buyer_email=buyer_info.get('email', ''),
            product_name=product_info.get('name', ''),
            product_id=product_info.get('id', 0),
            price=purchase_info.get('price', {}).get('value', 0),
            currency=purchase_info.get('price', {}).get('currency_value', 'BRL')
        )
        
        # Processa afiliados (se houver)
        new_affiliate_detected = False
        if affiliates_info:
            for affiliate_data in affiliates_info:
                affiliate_code = affiliate_data.get('affiliate_code', '')
                affiliate_name = affiliate_data.get('name', '')
                
                if affiliate_code and affiliate_name:
                    # Verifica se o afiliado já existe
                    existing_affiliate = Affiliate.query.filter_by(affiliate_code=affiliate_code).first()
                    
                    if existing_affiliate:
                        # Afiliado existente - atualiza contador de vendas
                        existing_affiliate.total_sales += 1
                        sale.affiliate_id = existing_affiliate.id
                    else:
                        # Novo afiliado detectado!
                        new_affiliate = Affiliate(
                            affiliate_code=affiliate_code,
                            name=affiliate_name,
                            first_sale_date=datetime.utcnow(),
                            total_sales=1,
                            is_new=True
                        )
                        db.session.add(new_affiliate)
                        db.session.flush()  # Para obter o ID
                        sale.affiliate_id = new_affiliate.id
                        new_affiliate_detected = True
                        
                        # Envia notificação em tempo real
                        send_realtime_notification({
                            'id': new_affiliate.id,
                            'name': affiliate_name,
                            'code': affiliate_code,
                            'first_sale_date': new_affiliate.first_sale_date.isoformat()
                        })
                        
                        print(f"🎉 NOVO AFILIADO DETECTADO: {affiliate_name} ({affiliate_code})")
        
        # Salva a venda no banco
        db.session.add(sale)
        db.session.commit()
        
        # Retorna resposta com informação se novo afiliado foi detectado
        response = {
            'message': 'Webhook processed successfully',
            'new_affiliate_detected': new_affiliate_detected,
            'transaction_id': sale.transaction_id
        }
        
        if new_affiliate_detected:
            response['affiliate_info'] = {
                'name': affiliate_name,
                'code': affiliate_code
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Erro ao processar webhook: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@webhook_bp.route('/test', methods=['POST'])
def test_webhook():
    """
    Endpoint para testar o sistema com dados simulados
    """
    try:
        # Dados de teste simulando um webhook da Hotmart
        test_data = {
            "event": "PURCHASE_APPROVED",
            "data": {
                "purchase": {
                    "transaction": f"TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "price": {
                        "value": 97.0,
                        "currency_value": "BRL"
                    }
                },
                "buyer": {
                    "name": "João Silva Teste",
                    "email": "joao.teste@email.com"
                },
                "product": {
                    "id": 123456,
                    "name": "Produto de Teste"
                },
                "affiliates": [
                    {
                        "affiliate_code": f"TEST{datetime.now().strftime('%H%M%S')}",
                        "name": f"Afiliado Teste {datetime.now().strftime('%H:%M:%S')}"
                    }
                ]
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
    affiliates_info = purchase_data.get('affiliates', [])
    
    # Cria registro da venda
    sale = Sale(
        transaction_id=purchase_info.get('transaction', ''),
        buyer_name=buyer_info.get('name', ''),
        buyer_email=buyer_info.get('email', ''),
        product_name=product_info.get('name', ''),
        product_id=product_info.get('id', 0),
        price=purchase_info.get('price', {}).get('value', 0),
        currency=purchase_info.get('price', {}).get('currency_value', 'BRL')
    )
    
    # Processa afiliados (se houver)
    new_affiliate_detected = False
    affiliate_name = ""
    affiliate_code = ""
    
    if affiliates_info:
        for affiliate_data in affiliates_info:
            affiliate_code = affiliate_data.get('affiliate_code', '')
            affiliate_name = affiliate_data.get('name', '')
            
            if affiliate_code and affiliate_name:
                # Verifica se o afiliado já existe
                existing_affiliate = Affiliate.query.filter_by(affiliate_code=affiliate_code).first()
                
                if existing_affiliate:
                    # Afiliado existente - atualiza contador de vendas
                    existing_affiliate.total_sales += 1
                    sale.affiliate_id = existing_affiliate.id
                else:
                    # Novo afiliado detectado!
                    new_affiliate = Affiliate(
                        affiliate_code=affiliate_code,
                        name=affiliate_name,
                        first_sale_date=datetime.utcnow(),
                        total_sales=1,
                        is_new=True
                    )
                    db.session.add(new_affiliate)
                    db.session.flush()  # Para obter o ID
                    sale.affiliate_id = new_affiliate.id
                    new_affiliate_detected = True
                    
                    # Envia notificação em tempo real
                    send_realtime_notification({
                        'id': new_affiliate.id,
                        'name': affiliate_name,
                        'code': affiliate_code,
                        'first_sale_date': new_affiliate.first_sale_date.isoformat()
                    })
                    
                    print(f"🎉 NOVO AFILIADO DETECTADO: {affiliate_name} ({affiliate_code})")
    
    # Salva a venda no banco
    db.session.add(sale)
    db.session.commit()
    
    # Retorna resposta com informação se novo afiliado foi detectado
    response = {
        'message': 'Webhook processed successfully',
        'new_affiliate_detected': new_affiliate_detected,
        'transaction_id': sale.transaction_id
    }
    
    if new_affiliate_detected:
        response['affiliate_info'] = {
            'name': affiliate_name,
            'code': affiliate_code
        }
    
    return jsonify(response), 200

