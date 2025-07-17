from django.urls import path

from .views import pizza_list, topping_list, ussd_order

urlpatterns = [
    path('pizzas/', pizza_list, name = 'pizza-list')
    ,path('toppings', topping_list, name = 'topping-list')
    ,path('order', ussd_order, name = 'ussd-order')

]