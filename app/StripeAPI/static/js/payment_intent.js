const stripe = Stripe(window.STRIPE_PUBLIC_KEY);
const elements = stripe.elements();
const style = {
  base: {
    color: "#32325d",
    fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
    fontSmoothing: "antialiased",
    fontSize: "16px",
    "::placeholder": {
      color: "#aab7c4"
    }
  },
  invalid: {
    color: "#fa755a",
    iconColor: "#fa755a"
  }
};

const cardNumber = elements.create("cardNumber", { style: style });
cardNumber.mount("#card-number");

const cardExpiry = elements.create("cardExpiry", { style: style });
cardExpiry.mount("#card-expiry");

const cardCvc = elements.create("cardCvc", { style: style });
cardCvc.mount("#card-cvc");

const form = document.getElementById("payment-form");
const clientSecret = document.getElementById("payment-form").dataset.clientSecret;

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const { error, paymentMethod } = await stripe.createPaymentMethod({
    type: "card",
    card: cardNumber,
  });
  if (error) {
    document.getElementById("error-message").innerText = error.message;
  } else {
    stripe.confirmCardPayment(clientSecret, {
      payment_method: paymentMethod.id
    }).then((result) => {
      if (result.error) {
        document.getElementById("error-message").innerText = result.error.message;
      } else if (result.paymentIntent && result.paymentIntent.status === "succeeded") {
        window.location.href = "/success/";
      }
    });
  }
});