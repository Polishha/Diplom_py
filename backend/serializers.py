from rest_framework import serializers
from .models import (
    User, Shop, Category, Product, ProductInfo,
    ProductParameter, Parameter, Contact, Order, OrderItem
)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone']
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'patronymic', 
                 'company', 'position', 'type', 'contacts', 'is_active']
        read_only_fields = ['id', 'is_active']


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'url', 'state']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'category']
        read_only_fields = ['id']


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()
    
    class Meta:
        model = ProductParameter
        fields = ['parameter', 'value']


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)
    parameters = ProductParameterSerializer(source='product_parameters', many=True, read_only=True)
    
    class Meta:
        model = ProductInfo
        fields = ['id', 'product', 'shop', 'model', 'external_id', 
                 'quantity', 'price', 'price_rrc', 'parameters']
        read_only_fields = ['id']


class OrderItemSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product_info', 'quantity']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemSerializer(many=True, read_only=True)
    contact = ContactSerializer(read_only=True)
    total_price = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'dt', 'state', 'contact', 'ordered_items', 'total_price']
        read_only_fields = ['id', 'dt']


class OrderConfirmSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    contact_id = serializers.IntegerField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    patronymic = serializers.CharField(required=False, allow_blank=True)
    company = serializers.CharField(required=False, allow_blank=True)
    position = serializers.CharField(required=False, allow_blank=True)
    type = serializers.ChoiceField(choices=['buyer', 'shop'], default='buyer')