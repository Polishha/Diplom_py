from django.urls import path
from .views import *

urlpatterns = [
    path('user/register', RegisterAccount.as_view(), name='user-register'),
    path('user/confirm', ConfirmAccount.as_view(), name='user-confirm'),
    path('user/login', LoginAccount.as_view(), name='user-login'),
    path('user/details', AccountDetails.as_view(), name='user-details'),
    
    path('password/reset', RequestPasswordReset.as_view(), name='password-reset'),
    path('password/reset/confirm', ConfirmPasswordReset.as_view(), name='password-reset-confirm'),
    
    path('categories', CategoryView.as_view(), name='categories'),
    path('shops', ShopView.as_view(), name='shops'),
    path('products', ProductInfoView.as_view(), name='products'),
    path('products/<int:pk>', ProductDetailView.as_view(), name='product-detail'),
    
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    
    path('basket', basket, name='basket'),
    
    path('contacts', ContactView.as_view(), name='contacts'),
    path('contacts/<int:pk>', ContactDetailView.as_view(), name='contact-detail'),
    
    path('orders', OrderView.as_view(), name='orders'),
    path('orders/<int:pk>', OrderDetailView.as_view(), name='order-detail'),
    path('orders/confirm', confirm_order, name='order-confirm'),
]