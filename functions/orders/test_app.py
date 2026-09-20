import pytest
from main import app as flask_app
import json
import os

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_reserve_status(client):
    """Testa se a rota de reserva responde com sucesso."""
    response = client.post('/reserve', 
                           data=json.dumps({'order_id': 'TEST-123'}),
                           content_type='application/json')
    assert response.status_code == 200
    assert response.json['status'] == 'reserved'

def test_ship_status(client):
    """Testa se a rota de envio responde com sucesso."""
    response = client.post('/ship', 
                           data=json.dumps({'order_id': 'TEST-123'}),
                           content_type='application/json')
    assert response.status_code == 200
    assert response.json['status'] == 'shipped'

def test_charge_no_secret_warning(client):
    """Testa a rota de pagamento quando o segredo não está no ambiente."""
    # Garante que a variável não está no ambiente de teste
    if 'STRIPE_API_KEY' in os.environ:
        del os.environ['STRIPE_API_KEY']
        
    response = client.post('/charge', 
                           data=json.dumps({'order_id': 'TEST-123'}),
                           content_type='application/json')
    assert response.status_code == 200
    assert response.json['status'] == 'charged'
