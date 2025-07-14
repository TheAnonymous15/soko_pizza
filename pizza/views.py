from rest_framework.decorators import api_view
from rest_framework.response import  Response
from rest_framework import status
from .models import Pizza, Topping, OrderItem, Order
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


@api_view(['POST'])
def place_order(request):
    data = request.data
    items_data = data.get('items', [])

    if not items_data:
        return Response({'error': 'No items provided'}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create()
    receipt = []

    for item in items_data:
        pizza_name = item.get('pizza')
        quantity = item.get('quantity', 1)
        topping_names = item.get('toppings', [])

        try:
            pizza = Pizza.objects.get(name__iexact=pizza_name)
        except Pizza.DoesNotExist:
            order.delete()  # fix: actually delete!
            return Response(
                {'error': f"Pizza '{pizza_name}' does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order_item = OrderItem.objects.create(
            order=order,
            pizza=pizza,
            quantity=quantity
        )

        valid_toppings = []
        for t_name in topping_names:
            try:
                topping = Topping.objects.get(name__iexact=t_name, pizza=pizza)
                valid_toppings.append(topping)
            except Topping.DoesNotExist:
                order.delete()
                return Response(
                    {'error': f"Topping '{t_name}' does not exist for pizza '{pizza_name}'"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        order_item.toppings.set(valid_toppings)

        # add to receipt
        receipt.append({
            "pizza": pizza.name,
            "quantity": quantity,
            "toppings": [t.name for t in valid_toppings],
            "item_total": f"{order_item.total_price:.2f}"
        })

    return Response({
        "order_id": order.id,
        "created_at": order.created_at,
        "subtotal": f"{order.subtotal:.2f}",
        "vat": f"{order.vat:.2f}",
        "total": f"{order.total:.2f}",
        "receipt": receipt
    }, status=status.HTTP_201_CREATED)