from django.db import models
from decimal import Decimal

VAT_RATE = Decimal('0.16')

class Pizza(models.Model):
    name = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'pizza'


class Topping(models.Model):
    CATEGORY_CHOICES = (
        ('basic', 'Basic'),
        ('deluxe', 'Deluxe'),
    )
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE, related_name='toppings')
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'pizza'


class Account(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    account_number = models.CharField(max_length=13, unique=True)
    account_balance = models.DecimalField(max_digits=50, decimal_places=2, default=0)

    def __str__(self):
        return f"Account {self.account_number} — Balance: {self.account_balance:.2f}"

    class Meta:
        app_label = 'pizza'


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    import uuid
    order_number = models.CharField(default=uuid.uuid4, max_length=20, editable=False, unique=True)
    payment_status = models.CharField(default="99", editable=False, max_length=2)


    def __str__(self):
        return f"Order: {self.order_number} \nPayment status: {self.payment_status} ({self.created_at.now()})"

    class Meta:
        app_label = 'pizza'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    toppings = models.ManyToManyField(Topping)

    @property
    def total_price(self):
        base = self.pizza.price
        topping_price = sum(t.price for t in self.toppings.all())
        return self.quantity * (base + topping_price)

    def __str__(self):
        return f"{self.quantity} x {self.pizza.name} in Order #{self.order.id}"

    class Meta:
        app_label = 'pizza'
