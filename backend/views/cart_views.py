from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from backend.models import Order, OrderItem, ProductInfo


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def basket(request):
    if request.method == 'GET':
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