import unittest
import json
from routes import app, cart, inventory


class BaseTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        cart.clear()

    def tearDown(self):
        cart.clear()

    def add(self, product_id):
        return self.client.post(
            '/api/cart/add',
            data=json.dumps({'product_id': product_id}),
            content_type='application/json'
        )

    def remove(self, product_id):
        return self.client.post(
            '/api/cart/remove',
            data=json.dumps({'product_id': product_id}),
            content_type='application/json'
        )

    def get_total(self):
        return self.client.get('/api/cart/total').get_json()



# CARRITO
# GET

class TestGetCarrito(BaseTest):

    def test_get_cart_vacio_retorna_200(self):
        res = self.client.get('/api/cart')
        self.assertEqual(res.status_code, 200)

    def test_get_cart_vacio_tiene_estructura(self):
        data = self.client.get('/api/cart').get_json()
        self.assertEqual(data['items'], [])
        self.assertEqual(data['total'], 0)
        self.assertEqual(data['count'], 0)


# ADD
class TestAgregarAlCarrito(BaseTest):

    def test_agregar_producto_existente(self):
        res = self.add(1)
        self.assertEqual(res.status_code, 200)

    def test_agregar_producto_inexistente_retorna_404(self):
        res = self.add(999)
        self.assertEqual(res.status_code, 404)

    def test_agregar_dos_veces_incrementa_cantidad(self):
        self.add(1)
        self.add(1)
        data = self.get_total()
        item = next(i for i in data['items'] if i['id'] == 1)
        self.assertEqual(item['quantity'], 2)

    def test_agregar_no_duplica_items(self):
        self.add(1)
        self.add(1)
        self.assertEqual(len(self.get_total()['items']), 1)


# REMOVE

class TestQuitarDelCarrito(BaseTest):

    def test_quitar_producto_que_no_esta_retorna_404(self):
        res = self.remove(1)
        self.assertEqual(res.status_code, 404)

    def test_quitar_decrementa_cantidad(self):
        self.add(2)
        self.add(2)
        self.remove(2)
        item = next(i for i in self.get_total()['items'] if i['id'] == 2)
        self.assertEqual(item['quantity'], 1)

    def test_quitar_ultima_unidad_elimina_item(self):
        self.add(3)
        self.remove(3)
        ids = [i['id'] for i in self.get_total()['items']]
        self.assertNotIn(3, ids)


# CLEAR

class TestVaciarCarrito(BaseTest):

    def test_clear_retorna_200(self):
        res = self.client.delete('/api/cart/clear')
        self.assertEqual(res.status_code, 200)

    def test_clear_vacia_el_carrito(self):
        self.add(1)
        self.client.delete('/api/cart/clear')
        self.assertEqual(self.get_total()['items'], [])


# TOTAL Y DESCUENTO
class TestTotal(BaseTest):

    def test_total_carrito_vacio_es_cero(self):
        data = self.get_total()
        self.assertEqual(data['subtotal'], 0)
        self.assertEqual(data['descuento'], 0)
        self.assertEqual(data['total'], 0)

    def test_total_calcula_correctamente(self):
        self.add(1)  # Producto 1: $4500
        data = self.get_total()
        self.assertEqual(data['subtotal'], 4500)
        self.assertEqual(data['total'], 4500)

    def test_descuento_no_aplica_bajo_15000(self):
        self.add(1) 
        self.assertEqual(self.get_total()['descuento'], 0)

    def test_descuento_aplica_sobre_15000(self):
        for _ in range(3):
            self.add(10)
        data = self.get_total()
        self.assertEqual(data['subtotal'], 21600)
        self.assertAlmostEqual(data['descuento'], 2160.0)
        self.assertAlmostEqual(data['total'], 19440.0)

    def test_cantidad_total_es_correcta(self):
        self.add(1)
        self.add(2)
        self.add(2)  # 2 unidades del producto 2
        self.assertEqual(self.get_total()['cantidad_total'], 3)



