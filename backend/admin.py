"""
Настройки административной панели Django.
Определяет, как модели отображаются и редактируются в админке.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Shop, Category, Product, ProductInfo,
    Parameter, ProductParameter, Contact, Order, OrderItem, ConfirmEmailToken
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Настройки отображения пользователей в админке.
    
    Позволяет просматривать и редактировать пользователей,
    фильтровать по типу и активности.
    
    List display:
        id, email, first_name, last_name, type, is_active
    
    List filter:
        type, is_active, is_staff
    
    Search fields:
        email, first_name, last_name
    """
    list_display = ('id', 'email', 'first_name', 'last_name', 'type', 'is_active')
    list_filter = ('type', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'patronymic', 'company', 'position')
        }),
        ('Права доступа', {
            'fields': ('type', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'type'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    """
    Настройки отображения магазинов в админке.
    
    List display:
        id, name, user, state
    
    List filter:
        state
    
    Search fields:
        name
    """
    list_display = ('id', 'name', 'user', 'state')
    list_filter = ('state',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Настройки отображения категорий в админке.
    
    List display:
        id, name
    
    Search fields:
        name
    
    Filter horizontal:
        shops (для удобного выбора магазинов)
    """
    list_display = ('id', 'name')
    search_fields = ('name',)
    filter_horizontal = ('shops',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Настройки отображения товаров в админке.
    
    List display:
        id, name, category
    
    List filter:
        category
    
    Search fields:
        name
    """
    list_display = ('id', 'name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)


class ProductParameterInline(admin.TabularInline):
    """
    Inline-редактирование параметров товара на странице товара.
    Позволяет редактировать параметры прямо в форме товара.
    """
    model = ProductParameter
    extra = 1


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    """
    Настройки отображения информации о товарах в админке.
    
    List display:
        id, product, shop, price, quantity
    
    List filter:
        shop
    
    Search fields:
        product__name, model
    
    Inlines:
        ProductParameterInline - для редактирования параметров
    """
    list_display = ('id', 'product', 'shop', 'price', 'quantity')
    list_filter = ('shop',)
    search_fields = ('product__name', 'model')
    inlines = [ProductParameterInline]


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    """
    Настройки отображения параметров в админке.
    
    List display:
        id, name
    
    Search fields:
        name
    """
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Настройки отображения контактов в админке.
    
    List display:
        id, user, city, street, house, phone
    
    List filter:
        city
    
    Search fields:
        user__email, city, phone
    """
    list_display = ('id', 'user', 'city', 'street', 'house', 'phone')
    list_filter = ('city',)
    search_fields = ('user__email', 'city', 'phone')


class OrderItemInline(admin.TabularInline):
    """
    Inline-редактирование позиций заказа на странице заказа.
    Позволяет просматривать и редактировать товары в заказе.
    """
    model = OrderItem
    extra = 1
    readonly_fields = ('product_info',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Настройки отображения заказов в админке.
    
    List display:
        id, user, dt, state, contact
    
    List filter:
        state
    
    Search fields:
        user__email
    
    Inlines:
        OrderItemInline - для просмотра товаров в заказе
    
    List editable:
        state - позволяет менять статус прямо из списка заказов
    
    Readonly fields:
        dt - дата создания заказа
    """
    list_display = ('id', 'user', 'dt', 'state', 'contact')
    list_filter = ('state',)
    search_fields = ('user__email',)
    inlines = [OrderItemInline]
    list_editable = ('state',)
    readonly_fields = ('dt',)


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    """
    Настройки отображения токенов подтверждения в админке.
    
    List display:
        id, user, created_at, key
    
    Search fields:
        user__email
    
    Readonly fields:
        created_at, key - нельзя редактировать
    """
    list_display = ('id', 'user', 'created_at', 'key')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'key')