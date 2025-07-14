from django.db import models
class Pizza(models.Model):
    name = models.CharField(max_length = 20)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name

class Topping(models.Model):
    CATEGORY_CHOICES = (
    ('basic', 'Basic'),
    ('deluxe', 'Deluxe')
    )
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE, related_name='toppings')
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name




# Create your models here.
