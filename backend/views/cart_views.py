"""
Представления для работы с корзиной покупателя.
Содержит функции для просмотра, добавления и удаления товаров из корзины.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from backend.models import Order, OrderItem, ProductInfo


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def basket(request):
    """
    Работа с корзиной пользователя.
    
    GET - просмотр содержимого корзины
    POST - добавление товаров в корзину
    DELETE - удаление товара из корзины
    
    GET /api/v1/basket
    
    Returns:
        200 OK: {
            "id": 1,
            "items": [
                {
                    "id": 1,
                    "product_info_id": 1,
                    "product_name": "Товар",
                    "shop_name": "Магазин",
                    "price": 1000,
                    "quantity": 2,
                    "sum": 2000
                }
            ],
            "total_sum": 2000
        }
    
    POST /api/v1/basket
    Request body:
        {
            "items": [
                {
                    "product_info_id": 1,
                    "quantity": 2
                }
            ]
        }
    
    Returns:
        200 OK: {"Status": True, "Message": "Товары добавлены в корзину"}
        400 Bad Request: {"Status": False, "Error": "Описание ошибки"}
    
    DELETE /api/v1/basket
    Request body:
        {
            "item_id": 1
        }
    
    Returns:
        200 OK: {"Status": True, "Message": "Товар удален из корзины"}
        400 Bad Request: {"Status": False, "Error": "Не указан ID товара"}
        404 Not Found: {"Status": False, "Error": "Товар не найден в корзине"}
    """
    if request.method == 'GET':
        """
        Просмотр содержимого корзины.
        
        Returns:
            Response: Информация о корзине или пустая корзина
        """
        try:
            order = Order.objects.get(
                user=request.user,
                state='basket'
            )
            
            items = []
            for item in order.ordered_items.all():
                items.append({
                    'id': item.id,
                    'product_info_id': item.product_info.id,
                    'product_name': item.product_info.product.name,
                    'shop_name': item.product_info.shop.name,
                    'price': item.product_info.price,
                    'quantity': item.quantity,
                    'sum': item.quantity * item.product_info.price
                })
            
            return Response({
                'id': order.id,
                'items': items,
                'total_sum': sum(item['sum'] for item in items)
            })
            
        except Order.DoesNotExist:
            return Response({'items': [], 'total_sum': 0})

    elif request.method == 'POST':
        """
        Добавление товаров в корзину.
        
        Args:
            request: HTTP запрос с массивом товаров для добавления
            
        Returns:
            Response: Результат операции
        """
        items_data = request.data.get('items')
        if not items_data:
            return Response(
                {'Status': False, 'Error': 'Не указаны товары'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            order, _ = Order.objects.get_or_create(
                user=request.user,
                state='basket'
            )

            for item in items_data:
                product_info_id = item.get('product_info_id')
                quantity = item.get('quantity', 1)

                try:
                    product_info = ProductInfo.objects.get(
                        id=product_info_id,
                        shop__state=True,
                        quantity__gte=quantity
                    )
                except ProductInfo.DoesNotExist:
                    return Response(
                        {'Status': False, 'Error': f'Товар {product_info_id} не найден или недостаточно количество'},
                        status=status.HTTP_404_NOT_FOUND
                    )

                OrderItem.objects.update_or_create(
                    order=order,
                    product_info=product_info,
                    defaults={'quantity': quantity}
                )

        return Response({'Status': True, 'Message': 'Товары добавлены в корзину'})

    elif request.method == 'DELETE':
        """
        Удаление товара из корзины.
        
        Args:
            request: HTTP запрос с ID товара для удаления
            
        Returns:
            Response: Результат операции
        """
        item_id = request.data.get('item_id')
        if not item_id:
            return Response(
                {'Status': False, 'Error': 'Не указан ID товара'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order_item = OrderItem.objects.get(
                id=item_id,
                order__user=request.user,
                order__state='basket'
            )
            order_item.delete()
            return Response({'Status': True, 'Message': 'Товар удален из корзины'})
        except OrderItem.DoesNotExist:
            return Response(
                {'Status': False, 'Error': 'Товар не найден в корзине'},
                status=status.HTTP_404_NOT_FOUND
            )