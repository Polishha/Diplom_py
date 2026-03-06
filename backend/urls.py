"""
URL-маршруты для API приложения backend.
Связывает URL-адреса с соответствующими представлениями.
"""

from django.urls import path
from .views import *

urlpatterns = [
    # Аутентификация
    path('user/register', RegisterAccount.as_view(), name='user-register'),
    path('user/confirm', ConfirmAccount.as_view(), name='user-confirm'),
    path('user/login', LoginAccount.as_view(), name='user-login'),
    path('user/details', AccountDetails.as_view(), name='user-details'),
    
    # Восстановление пароля
    path('password/reset', RequestPasswordReset.as_view(), name='password-reset'),
    path('password/reset/confirm', ConfirmPasswordReset.as_view(), name='password-reset-confirm'),
    
    # Товары и категории
    path('categories', CategoryView.as_view(), name='categories'),
    path('shops', ShopView.as_view(), name='shops'),
    path('products', ProductInfoView.as_view(), name='products'),
    path('products/<int:pk>', ProductDetailView.as_view(), name='product-detail'),
    
    # Для поставщиков (управление товарами)
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    
    # Для поставщиков (управление заказами)
    path('supplier/orders', get_supplier_orders, name='supplier-orders'),
    path('supplier/orders/<int:order_id>/status', update_order_status, name='update-order-status'),
    
    # Корзина
    path('basket', basket, name='basket'),
    
    # Контакты
    path('contacts', ContactView.as_view(), name='contacts'),
    path('contacts/<int:pk>', ContactDetailView.as_view(), name='contact-detail'),
    
    # Заказы
    path('orders', OrderView.as_view(), name='orders'),
    path('orders/<int:pk>', OrderDetailView.as_view(), name='order-detail'),
    path('orders/confirm', confirm_order, name='order-confirm'),
]