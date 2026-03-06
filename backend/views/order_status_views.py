"""
Представления для управления статусами заказов поставщиками.
Содержит функции для просмотра заказов поставщика и изменения их статусов.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from backend.models import Order, OrderItem, Shop


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """
    Обновление статуса заказа поставщиком.
    
    Доступно только для пользователей с типом 'shop' (поставщики).
    Поставщик может менять статус только тех заказов, которые содержат его товары.
    
    PATCH /api/v1/supplier/orders/{order_id}/status
    
    Args:
        request: HTTP запрос с полем 'status' в теле
        order_id: ID заказа для обновления
        
    Request body:
        {
            "status": "assembled"
        }
        
    Возможные статусы:
        - new: Новый
        - confirmed: Подтвержден
        - assembled: Собран
        - sent: Отправлен
        - delivered: Доставлен
        - canceled: Отменен
    
    Returns:
        200 OK: {
            "Status": True,
            "Message": "Статус заказа #1 изменен с \"new\" на \"assembled\""
        }
        400 Bad Request: {
            "Status": False,
            "Error": "Описание ошибки"
        }
        403 Forbidden: {
            "Status": False,
            "Error": "Только для поставщиков"
        }
        404 Not Found: {
            "Status": False,
            "Error": "Заказ не найден"
        }
    """
    # Проверяем, что пользователь - поставщик
    if request.user.type != 'shop':
        return Response(
            {'Status': False, 'Error': 'Только для поставщиков'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Проверяем наличие статуса в запросе
    new_status = request.data.get('status')
    if not new_status:
        return Response(
            {'Status': False, 'Error': 'Не указан статус'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Проверяем, что статус допустимый
    valid_statuses = ['new', 'confirmed', 'assembled', 'sent', 'delivered', 'canceled']
    if new_status not in valid_statuses:
        return Response(
            {'Status': False, 'Error': f'Недопустимый статус. Допустимые значения: {valid_statuses}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Получаем заказ
        order = Order.objects.get(id=order_id)
        
        # Проверяем, что заказ не в корзине
        if order.state == 'basket':
            return Response(
                {'Status': False, 'Error': 'Нельзя изменить статус корзины'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Получаем все магазины поставщика
        shops = Shop.objects.filter(user=request.user)
        
        # Проверяем, есть ли в заказе товары от магазинов этого поставщика
        order_items = OrderItem.objects.filter(
            order=order,
            product_info__shop__in=shops
        )
        
        if not order_items.exists():
            return Response(
                {'Status': False, 'Error': 'В этом заказе нет товаров вашего магазина'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Обновляем статус
        with transaction.atomic():
            old_status = order.state
            order.state = new_status
            order.save()
            
            # Здесь можно добавить отправку email уведомления покупателю
            # send_order_status_email(order.user.email, order, old_status, new_status)
        
        return Response({
            'Status': True,
            'Message': f'Статус заказа #{order.id} изменен с "{old_status}" на "{new_status}"'
        })
        
    except Order.DoesNotExist:
        return Response(
            {'Status': False, 'Error': 'Заказ не найден'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'Status': False, 'Error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_supplier_orders(request):
    """
    Получение списка заказов, содержащих товары поставщика.
    
    Доступно только для пользователей с типом 'shop' (поставщики).
    Возвращает только те заказы, в которых есть товары от магазинов поставщика.
    
    GET /api/v1/supplier/orders
    
    Returns:
        200 OK: [
            {
                "id": 1,
                "dt": "2024-01-01T12:00:00",
                "state": "new",
                "contact": {
                    "city": "Москва",
                    "street": "Тверская",
                    "phone": "+79991234567"
                },
                "supplier_items": [
                    {
                        "id": 1,
                        "product_name": "Товар",
                        "shop_name": "Мой магазин",
                        "price": 1000,
                        "quantity": 2,
                        "sum": 2000
                    }
                ],
                "total_supplier_sum": 2000
            }
        ]
    """
    if request.user.type != 'shop':
        return Response(
            {'Status': False, 'Error': 'Только для поставщиков'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Получаем все магазины поставщика
    shops = Shop.objects.filter(user=request.user)
    
    # Получаем все заказы, содержащие товары от этих магазинов
    orders = Order.objects.filter(
        ordered_items__product_info__shop__in=shops
    ).exclude(
        state='basket'
    ).distinct().order_by('-dt')
    
    # Формируем результат
    result = []
    for order in orders:
        # Получаем только товары этого поставщика в заказе
        supplier_items = order.ordered_items.filter(product_info__shop__in=shops)
        
        items_data = []
        for item in supplier_items:
            items_data.append({
                'id': item.id,
                'product_name': item.product_info.product.name,
                'shop_name': item.product_info.shop.name,
                'price': item.product_info.price,
                'quantity': item.quantity,
                'sum': item.quantity * item.product_info.price
            })
        
        result.append({
            'id': order.id,
            'dt': order.dt,
            'state': order.state,
            'contact': {
                'city': order.contact.city if order.contact else None,
                'street': order.contact.street if order.contact else None,
                'phone': order.contact.phone if order.contact else None
            } if order.contact else None,
            'supplier_items': items_data,
            'total_supplier_sum': sum(item['sum'] for item in items_data)
        })
    
    return Response(result)