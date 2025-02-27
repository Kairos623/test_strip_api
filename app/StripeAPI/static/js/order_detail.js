document.addEventListener("DOMContentLoaded", function () {
    const stripe = Stripe(window.STRIPE_PUBLIC_KEY);
    const buyButton = document.getElementById("buyOrderButton");

    if (buyButton) {
        buyButton.addEventListener("click", function () {
            const orderId = this.getAttribute("data-order-id");
            fetch(`/order/buy/${orderId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.sessionId) {
                        stripe.redirectToCheckout({ sessionId: data.sessionId })
                            .then(function(result) {
                                if (result.error) {
                                    console.error(result.error.message);
                                }
                            });
                    } else {
                        console.error("Ошибка: sessionId не получен", data);
                    }
                })
                .catch(error => console.error("Ошибка при создании сессии:", error));
        });
    }
});
