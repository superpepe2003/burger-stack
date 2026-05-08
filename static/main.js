// 1. Al cargar la página, traemos los productos
    document.addEventListener('DOMContentLoaded', () => {
        fetchProducts();
        updateCartDisplay();
    });

    async function fetchProducts() {
        const res = await fetch('/api/products');
        const products = await res.json();
        const menuDiv = document.getElementById('menu');
        
        menuDiv.innerHTML = products.map(p => `
            <div class="card" onclick="addToCart(${p.id})"  >
                <h3>${p.name}</h3>
                <p>${p.description}</p>
                <div class="price">$${p.price}</div>
            </div>
        `).join('');
    }

    // 2. Llamada al endpoint para agregar
    async function addToCart(productId) {
        await fetch('/api/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId })
        });
        updateCartDisplay();
    }

    // 2b. Llamada al endpoint para quitar
    async function removeFromCart(productId) {
        await fetch('/api/cart/remove', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId })
        });
        updateCartDisplay();
    }

    // 3. Llamada al endpoint de cálculo
    async function updateCartDisplay() {
        const res = await fetch('/api/cart/total');
        const data = await res.json();
        
        const sidebar = document.getElementById('sidebar');
        const cartContent = document.getElementById('cart-content');
        const subtotalEl = document.getElementById('subtotal');
        const discountEl = document.getElementById('discount');
        const totalEl = document.getElementById('total');

        if (data.items.length === 0) {
            sidebar.style.display = 'none';
        } else {
            sidebar.style.display = 'block';
            cartContent.innerHTML = data.items.map(item => `
                <div class="cart-item">
                    <span class="cart-item-name">${item.name}</span>
                    <div class="cart-item-controls">
                        <button class="btn-qty" onclick="removeFromCart(${item.id})">−</button>
                        <span class="qty">${item.quantity}</span>
                        <button class="btn-qty" onclick="addToCart(${item.id})">+</button>
                    </div>
                    <span class="cart-item-price">$${(item.price * item.quantity).toLocaleString()}</span>
                </div>
            `).join('');

            subtotalEl.innerText = `$${data.subtotal.toLocaleString()}`;
            discountEl.innerText = `-$${data.descuento.toLocaleString()}`;
            totalEl.innerText = `$${data.total.toLocaleString()}`;

            // Banner promo
            const promoEl = document.getElementById('promo-banner');
            if (data.subtotal >= 15000) {
                promoEl.textContent = '🎉 ¡Descuento del 10% aplicado!';
                promoEl.style.color = 'green';
            } else {
                const falta = (15000 - data.subtotal).toLocaleString();
                promoEl.textContent = `🏷️ ¡Agregá $${falta} más y conseguís 10% OFF!`;
                promoEl.style.color = '#e63946';
            }
        }
    }

    async function emptyCart() {
        await fetch('/api/cart/clear', { method: 'DELETE' });
        updateCartDisplay();
    }

    async function confirmOrder() {
        const res = await fetch('/api/cart/total');
        const data = await res.json();

        if (data.items.length === 0) {
            Swal.fire({
                icon: 'warning',
                title: 'Carrito vacío',
                text: 'Agregá productos antes de confirmar.',
                confirmButtonColor: '#e63946'
            });
            return;
        }

        const itemsHtml = data.items.map(item => `
            <tr>
                <td style="text-align:left">${item.name}</td>
                <td>${item.quantity}x</td>
                <td style="text-align:right">$${(item.price * item.quantity).toLocaleString()}</td>
            </tr>
        `).join('');

        const descuentoHtml = data.descuento > 0
            ? `<tr><td colspan="2" style="text-align:left; color:green">Descuento (10%)</td><td style="text-align:right; color:green">-$${data.descuento.toLocaleString()}</td></tr>`
            : '';

        Swal.fire({
            title: '🍔 Resumen del Pedido',
            html: `
                <table style="width:100%; border-collapse:collapse; font-size:0.95rem;">
                    <thead>
                        <tr style="border-bottom:2px solid #1d3557">
                            <th style="text-align:left">Producto</th>
                            <th>Cant.</th>
                            <th style="text-align:right">Precio</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${itemsHtml}
                        ${descuentoHtml}
                    </tbody>
                    <tfoot>
                        <tr style="border-top:2px solid #1d3557; font-weight:bold; font-size:1.1rem">
                            <td colspan="2" style="text-align:left">TOTAL</td>
                            <td style="text-align:right; color:#e63946">$${data.total.toLocaleString()}</td>
                        </tr>
                    </tfoot>
                </table>
            `,
            icon: 'success',
            confirmButtonText: '¡Hacer Pedido!',
            confirmButtonColor: '#e63946',
            showCancelButton: true,
            cancelButtonText: 'Cancelar'
        }).then(async (result) => {
            if (result.isConfirmed) {
                await fetch('/api/cart/clear', { method: 'DELETE' });
                updateCartDisplay();
                Swal.fire({
                    icon: 'success',
                    title: '¡Pedido confirmado!',
                    text: 'Tu pedido está en camino 🚀',
                    confirmButtonColor: '#e63946',
                    timer: 2500,
                    timerProgressBar: true
                });
            }
        });
    }