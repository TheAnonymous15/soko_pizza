from django.db import models
from decimal import Decimal

VAT_RATE = Decimal('0.16')

class Pizza(models.Model):
    name = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name


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


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def vat(self):
        return self.subtotal * VAT_RATE

    @property
    def total(self):
        return self.subtotal + self.vat

    def __str__(self):
        return f"Order #{self.id} ({self.created_at.date()})"


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
