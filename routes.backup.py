from flask import Flask, jsonify, request, render_template
from flasgger import Swagger

app = Flask(__name__)

swagger_config = {
    "headers": [],
    "specs": [{"endpoint": "apispec", "route": "/apispec.json"}],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}
swagger_template = {
    "info": {
        "title": "Burger Stack API",
        "description": "API REST para el sistema de pedidos de hamburguesas. Descuento del 10% en pedidos mayores a $15.000.",
        "version": "1.0.0"
    }
}
Swagger(app, config=swagger_config, template=swagger_template)

# Base de datos simulada
inventory = {
    1: {"id": 1, "name": "Clásica", "description": "Carne, lechuga, tomate y queso cheddar", "price": 4500},
    2: {"id": 2, "name": "Bacon Cheese", "description": "Doble carne, doble cheddar y mucho bacon", "price": 5800},
    3: {"id": 3, "name": "Crispy Chicken", "description": "Pollo rebozado, alioli y lechuga", "price": 4200},
    4: {"id": 4, "name": "Veggie Smash", "description": "Medallón de lentejas, palta y cebolla morada", "price": 4000},
    5: {"id": 5, "name": "Blue Burger", "description": "Carne, queso azul, cebolla caramelizada y nueces", "price": 6200},
    6: {"id": 6, "name": "Mexican Fire", "description": "Carne, guacamole, jalapeños y salsa picante", "price": 5500},
    7: {"id": 7, "name": "Mushrooms Choice", "description": "Carne, champiñones salteados y queso suizo", "price": 5900},
    8: {"id": 8, "name": "Egg-plosion", "description": "Carne, huevo frito, jamón y queso", "price": 5300},
    9: {"id": 9, "name": "BBQ Ribs Burger", "description": "Carne desmechada, salsa BBQ y coleslaw", "price": 6500},
    10: {"id": 10, "name": "Triple Smash", "description": "Tres medallones, cheddar y salsa secreta", "price": 7200}
}

cart = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    """
    Obtiene todos los productos del menú.
    ---
    tags:
      - Productos
    responses:
      200:
        description: Lista de productos disponibles
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              description:
                type: string
              price:
                type: number
    """
    return jsonify(list(inventory.values())), 200

@app.route('/api/cart', methods=['GET'])
def get_cart():
    """
    Obtiene el contenido actual del carrito.
    ---
    tags:
      - Carrito
    responses:
      200:
        description: Carrito actual con items, total y cantidad
        schema:
          type: object
          properties:
            items:
              type: array
            total:
              type: number
            count:
              type: integer
    """
    total = sum(item['price'] * item['quantity'] for item in cart)
    return jsonify({
        "items": cart,
        "total": total,
        "count": len(cart)
    }), 200

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    """
    Agrega un producto al carrito (o incrementa su cantidad).
    ---
    tags:
      - Carrito
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - product_id
          properties:
            product_id:
              type: integer
              example: 1
    responses:
      200:
        description: Carrito actualizado
      404:
        description: Producto no encontrado
    """
    data = request.json
    product_id = data.get('product_id')

    product = inventory.get(product_id)
    if not product:
        return jsonify({"error": "Producto no encontrado"}), 404

    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += 1
            return jsonify({"message": "Carrito actualizado", "cart": cart}), 200

    cart.append({
        "id": product["id"],
        "name": product["name"],
        "price": product["price"],
        "quantity": 1
    })

    return jsonify({"message": "Carrito actualizado", "cart": cart}), 200

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    """
    Quita una unidad de un producto del carrito (o lo elimina si queda en 0).
    ---
    tags:
      - Carrito
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - product_id
          properties:
            product_id:
              type: integer
              example: 1
    responses:
      200:
        description: Carrito actualizado
      404:
        description: Producto no encontrado en el carrito
    """
    data = request.json
    product_id = data.get('product_id')

    for item in cart:
        if item['id'] == product_id:
            if item['quantity'] > 1:
                item['quantity'] -= 1
            else:
                cart.remove(item)
            return jsonify({"message": "Carrito actualizado", "cart": cart}), 200

    return jsonify({"error": "Producto no encontrado en el carrito"}), 404

@app.route('/api/cart/clear', methods=['DELETE'])
def clear_cart():
    """
    Vacía el carrito por completo.
    ---
    tags:
      - Carrito
    responses:
      200:
        description: Carrito vaciado exitosamente
    """
    cart.clear()
    return jsonify({"message": "Carrito vaciado"}), 200

@app.route('/api/cart/total', methods=['GET'])
def calculate_total():
    """
    Calcula el total del carrito aplicando descuento si corresponde.
    ---
    tags:
      - Carrito
    responses:
      200:
        description: Resumen del carrito con subtotal, descuento y total
        schema:
          type: object
          properties:
            subtotal:
              type: number
            descuento:
              type: number
              description: 10% de descuento si subtotal supera $15.000
            total:
              type: number
            cantidad_total:
              type: integer
            items:
              type: array
    """
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    total_unidades = sum(item['quantity'] for item in cart)

    descuento = 0
    if subtotal > 15000:
        descuento = subtotal * 0.10

    total = subtotal - descuento

    return jsonify({
        "subtotal": subtotal,
        "descuento": descuento,
        "total": total,
        "cantidad_total": total_unidades,
        "items": cart
    })