from rest_framework import serializers
from .models import Pizza, Topping, Account

class PizzaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pizza
        fields = ['id', 'name', 'price']


class ToppingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topping
        fields = ['id', 'name', 'price']


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['account_number', 'account_balance']

