"""
Представления для работы с товарами, категориями и магазинами.
Содержит функции для просмотра каталога, фильтрации и импорта товаров.
"""

from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from requests import get
from yaml import load as load_yaml, Loader
from backend.models import ProductInfo, Category, Shop, Product, Parameter, ProductParameter
from backend.serializers import ProductInfoSerializer, CategorySerializer, ShopSerializer


class CategoryView(generics.ListAPIView):
    """
    Получение списка категорий товаров.
    
    GET /api/v1/categories
    
    Returns:
        200 OK: Список всех категорий в формате JSON
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None


class ShopView(generics.ListAPIView):
    """
    Получение списка активных магазинов.
    
    GET /api/v1/shops
    
    Returns:
        200 OK: Список магазинов, у которых state=True
    """
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class ProductInfoView(generics.ListAPIView):
    """
    Получение списка товаров с фильтрацией и поиском.
    
    GET /api/v1/products
    
    Query parameters:
        - shop_id: ID магазина
        - category_id: ID категории
        - price_min: минимальная цена
        - price_max: максимальная цена
        - search: поиск по названию
        - ordering: сортировка (price, -price, name, -name)
    
    Returns:
        200 OK: Список товаров, удовлетворяющих условиям фильтрации
    """
    serializer_class = ProductInfoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'shop_id': ['exact'],
        'product__category_id': ['exact'],
        'price': ['gte', 'lte'],
    }
    search_fields = ['product__name', 'model']
    ordering_fields = ['price', 'product__name']

    def get_queryset(self):
        """
        Получение queryset с оптимизацией запросов к БД.
        
        Returns:
            QuerySet: Товары с предзагруженными связанными данными
        """
        return ProductInfo.objects.filter(
            shop__state=True,
            quantity__gt=0
        ).select_related(
            'product', 'shop', 'product__category'
        ).prefetch_related('product_parameters__parameter')


class ProductDetailView(generics.RetrieveAPIView):
    """
    Получение детальной информации о конкретном товаре.
    
    GET /api/v1/products/{id}
    
    Args:
        id: ID товара (ProductInfo)
    
    Returns:
        200 OK: Детальная информация о товаре
        404 Not Found: Товар не найден
    """
    queryset = ProductInfo.objects.filter(
        shop__state=True,
        quantity__gt=0
    ).select_related(
        'product', 'shop', 'product__category'
    ).prefetch_related('product_parameters__parameter')
    serializer_class = ProductInfoSerializer
    permission_classes = [AllowAny]


class PartnerUpdate(APIView):
    """
    Обновление прайс-листа поставщика.
    
    Загружает YAML файл по URL или из загруженного файла,
    обновляет информацию о товарах магазина.
    
    POST /api/v1/partner/update
    
    Request body (form-data):
        - url: URL YAML файла с прайс-листом
        - или file: загруженный YAML файл
    
    Returns:
        200 OK: {
            "Status": True,
            "Message": "Прайс успешно обновлен"
        }
        400 Bad Request: {
            "Status": False,
            "Error": "Описание ошибки"
        }
        403 Forbidden: {
            "Status": False,
            "Error": "Только для магазинов"
        }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Обработка загрузки прайс-листа.
        
        Args:
            request: HTTP запрос с URL файла или самим файлом
            
        Returns:
            Response: Результат операции
        """
        if request.user.type != 'shop':
            return Response(
                {'Status': False, 'Error': 'Только для магазинов'},
                status=403
            )

        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return Response(
                    {'Status': False, 'Error': str(e)},
                    status=400
                )
            else:
                try:
                    stream = get(url).content
                    data = load_yaml(stream, Loader=Loader)

                    with transaction.atomic():
                        shop, _ = Shop.objects.get_or_create(
                            name=data['shop'], 
                            user_id=request.user.id
                        )
                        
                        # Создание/обновление категорий
                        for category in data['categories']:
                            category_object, _ = Category.objects.get_or_create(
                                id=category['id'], 
                                name=category['name']
                            )
                            category_object.shops.add(shop.id)
                            category_object.save()
                        
                        # Удаляем старую информацию о товарах
                        ProductInfo.objects.filter(shop_id=shop.id).delete()
                        
                        # Создаем новые товары
                        for item in data['goods']:
                            product, _ = Product.objects.get_or_create(
                                name=item['name'], 
                                category_id=item['category']
                            )

                            product_info = ProductInfo.objects.create(
                                product_id=product.id,
                                external_id=item['id'],
                                model=item.get('model', ''),
                                price=item['price'],
                                price_rrc=item['price_rrc'],
                                quantity=item['quantity'],
                                shop_id=shop.id
                            )
                            
                            # Добавляем параметры товара
                            for name, value in item.get('parameters', {}).items():
                                parameter_object, _ = Parameter.objects.get_or_create(name=name)
                                ProductParameter.objects.create(
                                    product_info_id=product_info.id,
                                    parameter_id=parameter_object.id,
                                    value=str(value)
                                )

                    return Response({'Status': True, 'Message': 'Прайс успешно обновлен'})

                except Exception as e:
                    return Response(
                        {'Status': False, 'Error': str(e)},
                        status=500
                    )

        return Response(
            {'Status': False, 'Errors': 'Не указан URL для загрузки'},
            status=400
        )