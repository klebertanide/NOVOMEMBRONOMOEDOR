from flask import Blueprint, Response, request
import json
import time
import threading
from queue import Queue

sse_bp = Blueprint('sse', __name__)

# Fila global para notificações em tempo real
notification_queue = Queue()
active_connections = []

class SSEConnection:
    def __init__(self):
        self.queue = Queue()
        self.active = True
        active_connections.append(self)
    
    def close(self):
        self.active = False
        if self in active_connections:
            active_connections.remove(self)

def broadcast_notification(data):
    """Envia notificação para todas as conexões ativas"""
    for connection in active_connections[:]:  # Cópia da lista para evitar problemas de concorrência
        if connection.active:
            try:
                connection.queue.put(data)
            except:
                connection.close()
        else:
            active_connections.remove(connection)

@sse_bp.route('/events')
def events():
    """Endpoint para Server-Sent Events"""
    def event_stream():
        connection = SSEConnection()
        
        try:
            # Envia evento inicial de conexão
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Conectado ao sistema de notificações'})}\n\n"
            
            while connection.active:
                try:
                    # Verifica se há notificações na fila
                    if not connection.queue.empty():
                        data = connection.queue.get(timeout=1)
                        yield f"data: {json.dumps(data)}\n\n"
                    else:
                        # Envia heartbeat a cada 30 segundos
                        yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time()})}\n\n"
                        time.sleep(30)
                except:
                    break
                    
        except GeneratorExit:
            connection.close()
        finally:
            connection.close()
    
    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )

@sse_bp.route('/broadcast', methods=['POST'])
def broadcast():
    """Endpoint para enviar notificações via SSE"""
    try:
        data = request.get_json()
        if data:
            broadcast_notification(data)
            return {'status': 'success', 'message': 'Notification broadcasted'}, 200
        else:
            return {'status': 'error', 'message': 'No data provided'}, 400
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@sse_bp.route('/connections')
def get_connections():
    """Retorna número de conexões ativas"""
    return {
        'active_connections': len(active_connections),
        'status': 'ok'
    }, 200

