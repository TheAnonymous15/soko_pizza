from django.contrib import admin
from .models import Topping, Pizza

admin.site.register(Pizza)
admin.site.register(Topping)