from django.urls import path

from .views import PizzaList, ToppingList, OrderView, MakePayment

urlpatterns = [
    path('v1/pizzas/', PizzaList.as_view(), name = 'pizza-list')
    ,path('v1/toppings/', ToppingList.as_view(), name = 'topping-list')
    ,path('v1/order/', OrderView.as_view(), name = 'post-order')
    ,path('v1/payment/', MakePayment.as_view(), name = 'make-payment')

]