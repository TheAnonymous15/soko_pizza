from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from decimal import Decimal

from .models import Order, OrderItem, Pizza, Topping
from .serializers import PizzaSerializer, ToppingSerializer


@api_view(['GET'])
def pizza_list(request):
    pizzas = Pizza.objects.all()  # type: ignore
    serializer = PizzaSerializer(pizzas, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def topping_list(request):
    size = request.GET.get('size')
    category = request.GET.get('category')
    toppings = Topping.objects.all()  # type: ignore
    if size:
        toppings = toppings.filter(pizza__name__iexact=size)
    if category:
        toppings = toppings.filter(category__iexact=category)
    serializer = ToppingSerializer(toppings, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def ussd_order(request):
    data = request.data
    session_id = data.get('session_id')
    selection = data.get('selection')

    if not session_id:
        return Response({"error": "Missing session_id"}, status=400)

    session_data = cache.get(session_id, {
        "state": "main_menu",
        "context": {}
    })
    state = session_data["state"]
    context = session_data["context"]

    # main menu
    if state == "main_menu":
        menu = "Welcome to SOKO PIZZA.\n1. Order pizza\n2. Exit"
        session_data["state"] = "main_menu_selection"
        cache.set(session_id, session_data)
        return Response({"menu": menu})

    if state == "main_menu_selection":
        if selection == '1':
            pizzas = Pizza.objects.all()  # type: ignore
            menu_lines = ["Select pizza size:"]
            for idx, p in enumerate(pizzas, start=1):
                menu_lines.append(f"{idx}. {p.name} - {int(p.price)}")
            session_data["state"] = "select_size"
            cache.set(session_id, session_data)
            return Response({"menu": "\n".join(menu_lines)})
        elif selection == '2':
            cache.delete(session_id)
            return Response({"menu": "Thank you for visiting SOKO PIZZA!"})
        else:
            return Response({"error": "Invalid selection"}, status=400)

    if state == "select_size":
        try:
            pizzas = list(Pizza.objects.all())  # type: ignore
            pizza = pizzas[int(selection) - 1]
            context.update({"pizza_id": pizza.id, "pizza_name": pizza.name})
            session_data.update({"state": "select_quantity", "context": context})
            cache.set(session_id, session_data)
            return Response({"menu": "Enter quantity:"})
        except (IndexError, ValueError):
            return Response({"error": "Invalid pizza selection"}, status=400)

    if state == "select_quantity":
        try:
            quantity = int(selection)
            if quantity <= 0:
                raise ValueError()
            context["quantity"] = quantity
            toppings = Topping.objects.all()  # type: ignore
            menu_lines = ["Select toppings (comma separated numbers):"]
            for idx, t in enumerate(toppings, start=1):
                menu_lines.append(f"{idx}. {t.name}")
            session_data.update({"state": "select_toppings", "context": context})
            cache.set(session_id, session_data)
            return Response({"menu": "\n".join(menu_lines)})
        except ValueError:
            return Response({"error": "Invalid quantity"}, status=400)

    if state == "select_toppings":
        try:
            toppings = list(Topping.objects.all())  # type: ignore
            selected_indices = [int(i.strip()) - 1 for i in selection.split(",")]
            topping_ids = [toppings[idx].id for idx in selected_indices]
            context["topping_ids"] = topping_ids

            pizza = Pizza.objects.get(id=context["pizza_id"])  # type: ignore
            quantity = context["quantity"]
            selected_toppings = Topping.objects.filter(id__in=topping_ids)  # type: ignore

            base_price = pizza.price
            topping_price = sum(t.price for t in selected_toppings)
            subtotal = quantity * (base_price + topping_price)
            vat = subtotal * Decimal("0.16")
            total = subtotal + vat

            topping_names = ", ".join(t.name for t in selected_toppings)

            summary = (
                f"Order summary:\n"
                f"Pizza: {pizza.name}\n"
                f"Quantity: {quantity}\n"
                f"Toppings: {topping_names}\n"
                f"Subtotal: {subtotal:.2f}\n"
                f"V.A.T: {vat:.2f}\n"
                f"Grand total: {total:.2f}\n"
                "Confirm order?\n1. Yes\n2. No"
            )
            session_data.update({"state": "confirm_order", "context": context})
            cache.set(session_id, session_data)
            return Response({"menu": summary})

        except (IndexError, ValueError):
            return Response({"error": "Invalid topping selection"}, status=400)

    if state == "confirm_order":
        if selection == '1':
            pizza = Pizza.objects.get(id=context["pizza_id"])  # type: ignore
            quantity = context["quantity"]
            toppings = Topping.objects.filter(id__in=context["topping_ids"])  # type: ignore

            order = Order.objects.create()  # type: ignore
            order_item = OrderItem.objects.create(order=order, pizza=pizza, quantity=quantity)  # type: ignore
            order_item.toppings.set(toppings)

            cache.delete(session_id)
            return Response({"menu": f"Order placed successfully. Order ID {order.id}"})
        elif selection == '2':
            cache.delete(session_id)
            return Response({"menu": "Order cancelled. Thank you!"})
        else:
            return Response({"error": "Invalid confirmation selection"}, status=400)

    return Response({"error": "Invalid state or selection"}, status=400)



@api_view(['GET'])
def make_order(request):
    pizza_id = request.GET.get("pizza_id")
    quantity = request.GET.get("quantity")
    toppings_str = request.GET.get("toppings", "")

    if not pizza_id or not quantity:
        return Response({"error": "pizza_id and quantity are required"}, status=400)

    try:
        pizza = Pizza.objects.get(id=int(pizza_id))
    except (Pizza.DoesNotExist, ValueError):
        return Response({"error": "Invalid pizza_id"}, status=400)

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError()
    except ValueError:
        return Response({"error": "Invalid quantity"}, status=400)

    topping_ids = []
    if toppings_str:
        try:
            topping_ids = [int(i.strip()) for i in toppings_str.split(",") if i.strip()]
        except ValueError:
            return Response({"error": "Invalid toppings list"}, status=400)

    toppings = Topping.objects.filter(id__in=topping_ids) if topping_ids else []

    base_price = pizza.price
    topping_price = sum(t.price for t in toppings)
    subtotal = quantity * (base_price + topping_price)
    vat = subtotal * Decimal("0.16")
    total = subtotal + vat

    order = Order.objects.create()
    order_item = OrderItem.objects.create(order=order, pizza=pizza, quantity=quantity)
    if toppings:
        order_item.toppings.set(toppings)

    receipt = {
        "order_id": order.id,
        "pizza": pizza.name,
        "quantity": quantity,
        "toppings": [t.name for t in toppings],
        "subtotal": f"{subtotal:.2f}",
        "vat": f"{vat:.2f}",
        "total": f"{total:.2f}"
    }

    return Response({"message": "Order placed successfully", "receipt": receipt})
