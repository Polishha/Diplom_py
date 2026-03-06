"""
Сериализаторы для преобразования моделей в JSON и обратно.
Определяют, какие поля моделей будут доступны через API и как они будут представлены.
"""

from rest_framework import serializers
from .models import (
    User, Shop, Category, Product, ProductInfo,
    ProductParameter, Parameter, Contact, Order, OrderItem
)


class ContactSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Contact.
    
    Преобразует контактные данные пользователя в JSON и обратно.
    
    Fields:
        id, city, street, house, structure, building, apartment, phone
    """
    class Meta:
        model = Contact
        fields = ['id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone']
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    
    Преобразует данные пользователя в JSON, включая связанные контакты.
    
    Fields:
        id, email, first_name, last_name, patronymic, company,
        position, type, contacts, is_active
    """
    contacts = ContactSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'patronymic', 
                 'company', 'position', 'type', 'contacts', 'is_active']
        read_only_fields = ['id', 'is_active']


class ShopSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Shop.
    
    Преобразует данные магазина в JSON.
    
    Fields:
        id, name, url, state
    """
    class Meta:
        model = Shop
        fields = ['id', 'name', 'url', 'state']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.
    
    Преобразует данные категории товаров в JSON.
    
    Fields:
        id, name
    """
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product.
    
    Преобразует данные товара в JSON, включая связанную категорию.
    
    Fields:
        id, name, category
    """
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'category']
        read_only_fields = ['id']


class ProductParameterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ProductParameter.
    
    Преобразует параметры товара в JSON.
    
    Fields:
        parameter, value
    """
    parameter = serializers.StringRelatedField()
    
    class Meta:
        model = ProductParameter
        fields = ['parameter', 'value']


class ProductInfoSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ProductInfo.
    
    Преобразует информацию о товаре в магазине в JSON,
    включая связанные данные о товаре, магазине и параметрах.
    
    Fields:
        id, product, shop, model, external_id, quantity, price, price_rrc, parameters
    """
    product = ProductSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)
    parameters = ProductParameterSerializer(source='product_parameters', many=True, read_only=True)
    
    class Meta:
        model = ProductInfo
        fields = ['id', 'product', 'shop', 'model', 'external_id', 
                 'quantity', 'price', 'price_rrc', 'parameters']
        read_only_fields = ['id']


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели OrderItem.
    
    Преобразует позицию заказа в JSON, включая информацию о товаре.
    
    Fields:
        id, product_info, quantity
    """
    product_info = ProductInfoSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product_info', 'quantity']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Order.
    
    Преобразует данные заказа в JSON, включая позиции заказа,
    контактную информацию и общую сумму.
    
    Fields:
        id, dt, state, contact, ordered_items, total_price
    """
    ordered_items = OrderItemSerializer(many=True, read_only=True)
    contact = ContactSerializer(read_only=True)
    total_price = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'dt', 'state', 'contact', 'ordered_items', 'total_price']
        read_only_fields = ['id', 'dt']


class OrderConfirmSerializer(serializers.Serializer):
    """
    Сериализатор для подтверждения заказа.
    
    Используется для валидации данных при подтверждении заказа.
    
    Fields:
        order_id: ID заказа (корзины)
        contact_id: ID контакта для доставки
    """
    order_id = serializers.IntegerField()
    contact_id = serializers.IntegerField()


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор для входа пользователя.
    
    Используется для валидации данных при входе в систему.
    
    Fields:
        email: Email пользователя
        password: Пароль (только для записи)
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class RegisterSerializer(serializers.Serializer):
    """
    Сериализатор для регистрации нового пользователя.
    
    Используется для валидации данных при регистрации.
    
    Fields:
        email: Email пользователя
        password: Пароль (минимум 8 символов)
        first_name: Имя
        last_name: Фамилия
        patronymic: Отчество (опционально)
        company: Компания (опционально)
        position: Должность (опционально)
        type: Тип пользователя (buyer/shop)
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    patronymic = serializers.CharField(required=False, allow_blank=True)
    company = serializers.CharField(required=False, allow_blank=True)
    position = serializers.CharField(required=False, allow_blank=True)
    type = serializers.ChoiceField(choices=['buyer', 'shop'], default='buyer')