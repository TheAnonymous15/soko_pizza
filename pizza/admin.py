from django.contrib import admin
from .models import Topping, Pizza, Order, Account

admin.site.register([Topping, Pizza, Order, Account])