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
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None


class ShopView(generics.ListAPIView):
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class ProductInfoView(generics.ListAPIView):
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
        return ProductInfo.objects.filter(
            shop__state=True,
            quantity__gt=0
        ).select_related(
            'product', 'shop', 'product__category'
        ).prefetch_related('product_parameters__parameter')


class ProductDetailView(generics.RetrieveAPIView):
    queryset = ProductInfo.objects.filter(
        shop__state=True,
        quantity__gt=0
    ).select_related(
        'product', 'shop', 'product__category'
    ).prefetch_related('product_parameters__parameter')
    serializer_class = ProductInfoSerializer
    permission_classes = [AllowAny]


class PartnerUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
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

                        for category in data['categories']:
                            category_object, _ = Category.objects.get_or_create(
                                id=category['id'], 
                                name=category['name']
                            )
                            category_object.shops.add(shop.id)
                            category_object.save()
                        
                        ProductInfo.objects.filter(shop_id=shop.id).delete()
                        
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