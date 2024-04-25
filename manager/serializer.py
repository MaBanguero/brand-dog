from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Order, Distributor, Task

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','password','email']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['email', 'customer_name', 'city', 'customer_address_2', 'customer_address',
                  'provider_address_2','provider_address',
                  'guide','price','status','buyer_platform', 'delivery_company']

class GetOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id','email', 'customer_name', 'city', 'customer_address_2', 'customer_address',
                  'provider_address_2','provider_address',
                  'guide','price','status','buyer_platform', 'delivery_company']
        
class DistributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distributor
        fields = ['full_name', 'delivery_company', 'telephone']

class GetDistributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distributor
        fields = ['id','full_name', 'delivery_company']