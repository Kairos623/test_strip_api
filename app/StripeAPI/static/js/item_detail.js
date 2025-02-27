document.addEventListener("DOMContentLoaded", function () {
    const stripe = Stripe(STRIPE_PUBLIC_KEY);

    const buyButton = document.getElementById("buyButton");
    if (buyButton) {
        buyButton.addEventListener("click", function () {
            const itemId = this.getAttribute("data-item-id");
            const quantity = document.getElementById("quantityInput").value;
            fetch(`/buy/${itemId}/?quantity=${quantity}`)
                .then(response => response.json())
                .then(data => {
                    if (data.sessionId) {
                        stripe.redirectToCheckout({ sessionId: data.sessionId });
                    } else {
                        console.error("Ошибка: sessionId не получен", data);
                    }
                })
                .catch(error => console.error("Ошибка при создании сессии:", error));
        });
    }

    const addToOrderForm = document.getElementById('add-to-order-form');
    if (addToOrderForm) {
        addToOrderForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const form = this;
            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => response.json())
                .then(data => {
                    const messageDiv = document.getElementById('message');
                    if (data.status === 'error') {
                        messageDiv.innerHTML = '<div class="alert alert-danger" role="alert">' + data.message + '</div>';
                    } else {
                        messageDiv.innerHTML = '<div class="alert alert-success" role="alert">' + data.message + '</div>';
                    }
                })
                .catch(error => console.error('Ошибка:', error));
        });
    }
});

