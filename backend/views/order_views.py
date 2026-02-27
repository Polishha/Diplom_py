from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from backend.models import Order, Contact
from backend.serializers import OrderSerializer


class OrderView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).exclude(
            state='basket'
        ).prefetch_related(
            'ordered_items__product_info__product',
            'ordered_items__product_info__shop'
        ).order_by('-dt')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related(
            'ordered_items__product_info__product',
            'ordered_items__product_info__shop',
            'ordered_items__product_info__product_parameters__parameter'
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_order(request):
    order_id = request.data.get('order_id')
    contact_id = request.data.get('contact_id')

    if not order_id or not contact_id:
        return Response(
            {'Status': False, 'Error': 'Не указаны ID заказа или контакта'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():
            order = Order.objects.get(
                id=order_id,
                user=request.user,
                state='basket'
            )
            
            contact = Contact.objects.get(
                id=contact_id,
                user=request.user
            )
            
            if not order.ordered_items.exists():
                return Response(
                    {'Status': False, 'Error': 'Корзина пуста'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            order.contact = contact
            order.state = 'new'
            order.save()
            
            send_order_confirmation_email(request.user.email, order)
            
            return Response(
                {'Status': True, 'Message': 'Заказ подтвержден', 'Order_id': order.id},
                status=status.HTTP_200_OK
            )
            
    except Order.DoesNotExist:
        return Response(
            {'Status': False, 'Error': 'Корзина не найдена'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Contact.DoesNotExist:
        return Response(
            {'Status': False, 'Error': 'Контакт не найден'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'Status': False, 'Error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def send_order_confirmation_email(user_email, order):
    subject = f'Подтверждение заказа №{order.id}'
    
    items_list = []
    total_sum = 0
    for item in order.ordered_items.all():
        item_sum = item.quantity * item.product_info.price
        total_sum += item_sum
        items_list.append(
            f"- {item.product_info.product.name} x {item.quantity} = {item_sum} руб."
        )
    
    items_text = '\n'.join(items_list)
    
    message = f'''
    Ваш заказ №{order.id} подтвержден.
    
    Состав заказа:
    {items_text}
    
    Итого: {total_sum} руб.
    
    Адрес доставки: {order.contact}
    
    Статус заказа: Новый
    
    Спасибо за покупку!
    '''
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )