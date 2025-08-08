from datetime import datetime
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem, Pizza, Topping, Account
from .serializers import PizzaSerializer, ToppingSerializer, AccountSerializer


class PizzaList(APIView):
    def get(self, request):
        pizzas = Pizza.objects.all()  # type: ignore
        serializer = PizzaSerializer(pizzas, many=True)
        return Response({
            "statusCode": "00",
            "statusMessage": "Success",
            "successful": True,
            "responseObject": serializer.data
        }, status=status.HTTP_200_OK)


class ToppingList(APIView):
    def get(self, request):
        size = request.query_params.get("size")
        category = request.query_params.get("category")
        toppings = Topping.objects.all()  # type: ignore
        if size:
            toppings = toppings.filter(pizza__name__iexact=size)

        if category:
            toppings = toppings.filter(category__iexact=category)

        serializer = ToppingSerializer(toppings, many=True)

        return Response({
            "statusCode": "00",
            "statusMessage": "Success",
            "successful": True,
            "responseObject": serializer.data
        }, status=status.HTTP_200_OK)

class OrderView(APIView):
    def post(self, request):
        data = request.data
        pizza_id = data.get("pizza_id")
        quantity = data.get("quantity")
        topping_list = data.get("toppings", [])

        if not all([pizza_id, quantity]):
            return Response({
                "statusCode": "99",
                "statusMessage": "Pizza ID and quantity are required",
                "successful": False,
                "responseObject": []
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            pizza = Pizza.objects.get(id=int(pizza_id))  # type: ignore
        except (Pizza.DoesNotExist, ValueError):  # type: ignore
            return Response({
                "statusCode": "99",
                "statusMessage": "Invalid pizza ID",
                "successful": False,
                "responseObject": None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            return Response({
                "statusCode": "99",
                "statusMessage": "Invalid quantity",
                "successful": False,
                "responseObject": None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            if topping_list:
                if not isinstance(topping_list, list):
                    return Response({
                        "statusCode": "99",
                        "statusMessage": "Toppings must be a list of IDs",
                        "successful": False,
                        "responseObject": None
                    }, status=status.HTTP_400_BAD_REQUEST)

                topping_ids = [int(t) for t in topping_list]
                toppings = Topping.objects.filter(id__in=topping_ids)  # type: ignore
            else:
                toppings = []

            base_price = pizza.price
            topping_price = sum(t.price for t in toppings)
            subtotal = quantity * (base_price + topping_price)
            vat = Decimal("0.16") * subtotal
            total = subtotal + vat
            order_number = f"OR{datetime.now().strftime('%Y%m%d%H%M%S')}"

            order = Order.objects.create(  # type: ignore
                subtotal=subtotal,
                vat=vat,
                total=total,
                order_number=order_number
            )

            order_item = OrderItem.objects.create(order=order, pizza=pizza, quantity=quantity)  # type: ignore
            if toppings:
                order_item.toppings.set(toppings)

            receipt = {
                "order_id": order_number,
                "pizza": pizza.name,
                "quantity": quantity,
                "toppings": [t.name for t in toppings],
                "subtotal": f"{subtotal:.2f}",
                "vat": f"{vat:.2f}",
                "grand_total": f"{total:.2f}"
            }

            return Response(
                {
                "statusCode": "00",
                "statusMessage": f"Order {order_number} processed successfully",
                "successful": True,
                "responseObject": receipt
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "statusCode": "99",
                "statusMessage": f"Unknown error occurred: {str(e)}",
                "successful": False,
                "responseObject": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MakePayment(APIView):
    def post(self, request):
        data = request.data
        account_number = data.get("account_number")
        amount = data.get("amount")
        order_id = data.get("order_id")

        if not all([account_number, amount, order_id]):
            return Response({
                "statusCode": "99",
                "statusMessage": "Account number, order_id and amount are required",
                "successful": False,
                "responseObject": None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError
        except:
            return Response({
                "statusCode": "99",
                "statusMessage": "Invalid amount",
                "successful": False,
                "responseObject": None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(order_number=order_id)  # type: ignore
        except Order.DoesNotExist:  # type: ignore
            return Response({
                "statusCode": "99",
                "statusMessage": "Order not found",
                "successful": False,
                "responseObject": None
            }, status=status.HTTP_400_BAD_REQUEST)


        try:
            account = Account.objects.get(account_number=account_number)  # type: ignore
        except Account.DoesNotExist:  # type: ignore


        if order.payment_status == "00":
            return Response({
                "statusCode": "99",
                "statusMessage": "Payment for the order already completed",
                "successful": False,
                "responseObject": None
            }, status=status.HTTP_400_BAD_REQUEST)

        if not order.total == amount:
            return Response({
                "statusCode": "99",
                "statusMessage": "Wrong amount submitted for payment",
                "successful": False,
                "responseObject": None
            }, status=status.HTTP_400_BAD_REQUEST)

        if account.account_balance < amount:
            return Response({
                "statusCode": "99",
                "statusMessage": "Insufficient balance",
                "successful": False,
                "responseObject": None
            }, status=status.HTTP_400_BAD_REQUEST)


        try:
            account.account_balance -= amount
            order.payment_status = "00"
            for item in [account, order]:
                item.save()

            return Response({
                "statusCode": "00",
                "statusMessage": f"Payment completed for Order number {order.order_number}",
                "successful": True,
                "responseObject": AccountSerializer(account).data
            }, status=status.HTTP_200_OK)


        except Exception as e:
            return Response({
                "statusCode": "99",
                "statusMessage": f"Payment processing failed with error: {e}",
                "successful": False,
                "responseObject": None
            }, status=status.HTTP_400_BAD_REQUEST)
