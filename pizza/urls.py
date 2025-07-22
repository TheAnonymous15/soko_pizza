from django.urls import path

from .views import pizza_list, topping_list, ussd_order, make_order, post_order, make_payment

urlpatterns = [
    path('pizzas', pizza_list, name = 'pizza-list')
    ,path('toppings', topping_list, name = 'topping-list')
    ,path('order', post_order, name = 'post-order')
    ,path('new_order', make_order, name = 'make-order')
    ,path('payment', make_payment, name = 'make-payment')

]