from rest_framework.decorators import api_view
from rest_framework.response import  Response
from .models import Pizza, Topping
from .serializers import PizzaSerializer, ToppingSerializer


@api_view(['GET'])
def pizza_list(request):
    pizzas = Pizza.objects.all() # type: ignore
    serializer  = PizzaSerializer(pizzas, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def topping_list(request):
    size = request.GET.get('size')
    category = request.GET.get('category')
    toppings = Topping.objects.all() # type: ignore
    if size:
        toppings = toppings.filter(pizza__name__iexact=size)
    if category:
        toppings = toppings.filter(category__iexact=category)
    serializer = ToppingSerializer(toppings, many = True)
    return Response(serializer.data)