
// === GLOBAL UTILITIES ===
const CART_KEY = 'cartCounts';

function loadCart() {
    return JSON.parse(localStorage.getItem(CART_KEY) || '{}');
}
function saveCart(cart) {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
}
function clearCart() {
    localStorage.setItem(CART_KEY, '{}');
}

async function fetchProducts() {
    try {
        const res = await fetch(`${window.location.origin}/products`);
        console.log("📡 Response:", res);

        if (!res.ok) {
            throw new Error(`Server returned ${res.status}`);
        }

        const data = await res.json();
        console.log("Получено из бэкенда:", data);
        return data;
    } catch (e) {
        console.error("Не удалось загрузить товары с backend. Используется мок.", e);
        return Array.from({ length: 28 }, (_, i) => ({
            id: i + 1,
            name: `Лампочка ${i + 1}`,
            image: 'https://img.lu.ru/add_photo/big/l/f/y/lfy_7560_t_2.jpg',
            description: `Подробное описание лампочки ${i + 1}. Энергосберегающая LED-лампа, срок службы 25000 часов.`,
            cost: Math.floor(100 + Math.random() * 500),
            wattage: [5, 7, 10, 15][Math.floor(Math.random() * 4)]
        }));
    }
}

// function parseAttributes(product) {
//     if (!product || !product.attributes) return {};
//     try {
//         return typeof product.attributes === "string"
//             ? JSON.parse(product.attributes)
//             : product.attributes;
//     } catch (e) {
//         console.error("Ошибка парсинга атрибутов:", e);
//         return {};
//     }
// }


async function submitOrder(formData, cart) {
    const customerRes = await fetch("/orders/customers", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: formData.fullName,
            email: formData.email,
            phone: formData.phone
        })
    });
    const customer = await customerRes.json();

    const items = Object.entries(cart)
        .filter(([_, quantity]) => parseInt(quantity) > 0)
        .map(([id, quantity]) => ({
            product_id: parseInt(id),
            product_quantity: parseInt(quantity)
        }));

    if (items.length === 0) {
        alert("Корзина пуста. Добавьте товары перед оформлением заказа.");
        throw new Error("Корзина пуста");
    }

    console.log("📦 Отправляем заказ:", {
        customer_id: customer.id,
        address: formData.address,
        information: formData.comment,
        items
    });

    const orderRes = await fetch("/orders/orders", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            customer_id: customer.id,
            address: formData.address,
            information: formData.comment,
            items
        })
    });


    return await orderRes.json();
}

document.addEventListener('DOMContentLoaded', async () => {
    const cart = loadCart();
    const products = await fetchProducts();
    const orderTotalEl = document.getElementById('orderTotal');
    if (orderTotalEl) {
        const total = Object.entries(cart).reduce((sum, [id, quantity]) => {
            const product = products.find(p => p.id === parseInt(id));
            return sum + (product ? parseFloat(product.cost) * quantity : 0);
        }, 0);
        orderTotalEl.textContent = `${total.toFixed(2)} руб.`;
    }
    // === Главная страница ===
    if (document.getElementById('cardsContainer')) {
        const container = document.getElementById('cardsContainer');
        const showMoreBtn = document.getElementById('showMoreBtn');

        function createCountInput(productId) {
            const input = document.createElement('input');
            input.type = 'number';
            input.min = 0;
            input.className = 'count-input';
            input.value = cart[productId] || '';
            return input;
        }

        function createCard(product) {
            const card = document.createElement('div');
            card.className = 'card';

            const imgLink = document.createElement('a');
            imgLink.href = `card.html?id=${product.id}`;
            const img = document.createElement('img');
            img.src = product.image_url || product.image;
            img.alt = product.name;
            imgLink.appendChild(img);

            const bottom = document.createElement('div');
            bottom.className = 'card-bottom';

            const titleLink = document.createElement('a');
            titleLink.href = `card.html?id=${product.id}`;
            titleLink.className = 'card-title';
            titleLink.textContent = product.name;

            const btnGroup = document.createElement('div');
            btnGroup.className = 'btn-group';
            const minusBtn = document.createElement('button');
            minusBtn.className = 'control-btn';
            minusBtn.textContent = '-';
            const input = createCountInput(product.id);
            const plusBtn = document.createElement('button');
            plusBtn.className = 'control-btn';
            plusBtn.textContent = '+';

            plusBtn.addEventListener('click', () => {
                let value = parseInt(input.value) || 0;
                cart[product.id] = ++value;
                input.value = value;
                saveCart(cart);
            });

            minusBtn.addEventListener('click', () => {
                let value = parseInt(input.value) || 0;
                value = Math.max(0, --value);
                input.value = value || '';
                if (value > 0) cart[product.id] = value;
                else delete cart[product.id];
                saveCart(cart);
            });

            btnGroup.append(minusBtn, input, plusBtn);
            bottom.append(titleLink, btnGroup);
            card.append(imgLink, bottom);
            return card;
        }

        function renderCards(count) {
            container.innerHTML = '';
            products.slice(0, count).forEach(p => container.appendChild(createCard(p)));
        }

        renderCards(16);
        if (products.length <= 16) showMoreBtn.style.display = 'none';
        showMoreBtn.addEventListener('click', () => {
            renderCards(products.length);
            showMoreBtn.style.display = 'none';
        });
    }

    // === Страница карточки товара ===
    if (document.getElementById('productDetails')) {
        const productId = parseInt(new URLSearchParams(window.location.search).get('id'));
        const product = products.find(p => p.id === productId);
        const container = document.getElementById('productDetails');

        if (product) {
            container.innerHTML = `
                <div class="product-image-container">
                    <img src="${product.image_url || product.image || "fallback.jpg"}" alt="${product.name}" class="product-image">
                    <h1 class="product-title">${product.name}</h1>
                </div>
                <div class="product-info">
                    <div class="product-header">
                        <li>Цена: ${product.cost} руб.</li>
                        <div class="cart-controls">
                            <span class="cart-label">В корзину:</span>
                            <button class="quantity-btn minus">-</button>
                            <input type="number" min="1" value="${cart[productId] != null ? cart[productId] : ''}" class="quantity-input">
                            <button class="quantity-btn plus">+</button>
                        </div>
                    </div>
                    <div class="product-description">
                        <h2>Описание:</h2>
                        <p>${product.description}</p>
                    </div>
                    <div class="product-specs">
                        <h2>Характеристики:</h2>
                        <ul>
                            <li>Мощность: ${product.attributes?.power || "не указана"} Вт</li>
                            <li>Цвет: ${product.attributes?.color || "не указан"}</li>
                        </ul>
                    </div>
                </div>
            `;

            const qtyInput = container.querySelector('.quantity-input');
            const plusBtn = container.querySelector('.plus');
            const minusBtn = container.querySelector('.minus');

            plusBtn.addEventListener('click', () => {
                qtyInput.value = ++qtyInput.value;
                cart[productId] = +qtyInput.value;
                saveCart(cart);
            });

            minusBtn.addEventListener('click', () => {
                qtyInput.value = Math.max(0, --qtyInput.value);
                if (+qtyInput.value <= 0) delete cart[productId];
                else cart[productId] = +qtyInput.value;
                saveCart(cart);
            });

            qtyInput.addEventListener('input', () => {
                let v = parseInt(qtyInput.value) || 0;
                if (v > 0) cart[productId] = v;
                else delete cart[productId];
                saveCart(cart);
            });
        } else {
            container.innerHTML = '<p class="not-found">Товар не найден</p>';
        }
    }

    // === Корзина ===
    if (document.getElementById('cartBody')) {
        const cartBody = document.getElementById('cartBody');
        const totalSum = document.getElementById('totalSum');

        function updateTotal() {
            const sum = Array.from(cartBody.querySelectorAll('tr')).reduce((acc, tr) => acc + parseInt(tr.children[3].textContent), 0);
            totalSum.textContent = sum;
        }

        Object.entries(cart).forEach(([id, count]) => {
            const prod = products.find(p => p.id === +id);
            if (!prod) return;

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${prod.name}</td>
                <td>${prod.cost}</td>
                <td>
                    <button class="quantity-btn minus">-</button>
                    <input type="number" min="0" value="${count}" class="quantity-input"/>
                    <button class="quantity-btn plus">+</button>
                </td>
                <td>${prod.cost * count}</td>
                <td><button class="remove-btn">×</button></td>
            `;
            cartBody.append(row);

            const input = row.querySelector('.quantity-input');
            const tdSum = row.children[3];

            function refresh(newCount) {
                if (newCount <= 0) {
                    delete cart[id];
                    row.remove();
                } else {
                    cart[id] = newCount;
                    input.value = newCount;
                    tdSum.textContent = prod.cost * newCount;
                }
                saveCart(cart);
                updateTotal();
            }

            row.querySelector('.plus').addEventListener('click', () => refresh(+input.value + 1));
            row.querySelector('.minus').addEventListener('click', () => refresh(+input.value - 1));
            input.addEventListener('change', () => refresh(+input.value));
            row.querySelector('.remove-btn').addEventListener('click', () => refresh(0));
        });

        updateTotal();

        document.getElementById('orderBtn').addEventListener('click', () => {
            window.location.href = 'placing_order.html';
        });
    }

    // === Оформление ===
    if (document.getElementById('orderForm')) {
        const form = document.getElementById('orderForm');
        const confirmationDiv = document.getElementById('orderConfirmation');
        const orderNumberSpan = document.getElementById('orderNumber');
        const backToMainBtn = document.getElementById('backToMainBtn');

        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const formData = {
                fullName: this.fullName.value,
                email: this.email.value,
                phone: this.phone.value,
                address: this.address.value,
                comment: this.comment.value
            };
            try {
                const order = await submitOrder(formData, cart);
                clearCart();
                form.style.display = 'none';
                confirmationDiv.style.display = 'block';
                orderNumberSpan.textContent = `Номер заказа: ${order.number}`;
            } catch (err) {
                alert("Ошибка при отправке заказа.");
                console.error(err);
            }
        });

        if (backToMainBtn) {
            backToMainBtn.addEventListener('click', () => {
                window.location.href = 'main.html';
            });
        }
    }
});
