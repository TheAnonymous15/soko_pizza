from django.urls import path
from .views import pizza_list, topping_list

urlpatterns = [
    path('pizzas/', pizza_list, name = 'pizza-list')
    ,path('toppings', topping_list, name = 'topping-list')
]