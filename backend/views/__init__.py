"""
Инициализация пакета views.
Экспортирует все классы и функции представлений для удобного импорта.
"""

from .auth_views import RegisterAccount, ConfirmAccount, LoginAccount, AccountDetails
from .product_views import CategoryView, ShopView, ProductInfoView, ProductDetailView, PartnerUpdate
from .cart_views import basket
from .contact_views import ContactView, ContactDetailView
from .order_views import OrderView, OrderDetailView, confirm_order
from .password_views import RequestPasswordReset, ConfirmPasswordReset
from .order_status_views import update_order_status, get_supplier_orders