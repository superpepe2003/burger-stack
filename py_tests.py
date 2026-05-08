import pytest
import json
from routes import app, cart

@pytest.fixture
def client():
    app.config['TESTING'] = True
    cart.clear()
    yield app.test_client()
    cart.clear()

def add(client, product_id):
    return client.post('/api/cart/add', data=json.dumps({'product_id': product_id}), content_type='application/json')

def get_total(client):
    return client.get('/api/cart/total').get_json()

# GET
def test_get_cart_vacio_retorna_200(client):
    assert client.get('/api/cart').status_code == 200

def test_get_cart_vacio_tiene_estructura(client):
    data = client.get('/api/cart').get_json()
    assert data['items'] == []
    assert data['total'] == 0
    assert data['count'] == 0

# ADD
def test_agregar_producto_existente(client):
    assert add(client, 1).status_code == 200

def test_agregar_producto_inexistente_retorna_404(client):
    assert add(client, 999).status_code == 404

def test_agregar_no_duplica_items(client):
    add(client, 1)
    add(client, 1)
    assert len(get_total(client)['items']) == 1

# REMOVE
def test_quitar_producto_que_no_esta_retorna_404(client):
    assert client.post('/api/cart/remove', data=json.dumps({'product_id': 1}), content_type='application/json').status_code == 404

# TOTAL
def test_descuento_aplica_sobre_15000(client):
    for _ in range(3):
        add(client, 10)
    data = get_total(client)
    assert data['subtotal'] == 21600
    assert data['descuento'] == pytest.approx(2160.0)