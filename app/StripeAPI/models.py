from django.db import models
from decimal import Decimal


class Item(models.Model):
    CURRENCY_CHOICES = [
        ('usd', 'USD'),
        ('eur', 'EUR'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='usd')

    objects = models.Manager()

    def __str__(self):
        return f"{self.name} ({self.currency.upper()})"


class Discount(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Процент купона со Stripe, на пример 15%"
    )
    stripe_coupon_id = models.CharField(
        max_length=100,
        help_text="ID купона в Stripe, например '25OFF'"
    )

    def __str__(self):
        return self.name


class Tax(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Налоговая ставка в процентах со Stripe, например 8.25"
    )
    stripe_tax_rate_id = models.CharField(
        max_length=100,
        help_text="ID налоговой ставки в Stripe, например 'txr_1Hh1YZ2eZvKYlo2C3'"
    )

    objects = models.Manager()

    def __str__(self):
        return self.name


class Order(models.Model):
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True, default=1)
    paid = models.BooleanField(default=False)

    objects = models.Manager()

    @property
    def base_amount(self):
        return sum(item.total_price for item in self.order_items.all())

    @property
    def total_amount(self):
        base = self.base_amount

        # Calculate discount
        if self.discount:
            discount_amount = base * (self.discount.percentage / Decimal('100'))
        else:
            discount_amount = Decimal('0')
        base = base - discount_amount

        if self.tax:
            tax_amount = base * (self.tax.percentage / Decimal('100'))
        else:
            tax_amount = Decimal('0')

        return base + tax_amount

    def __str__(self):
        return f"Order {self.id} - Total: ${self.total_amount}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.item.price * self.quantity

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"