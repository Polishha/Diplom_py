from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Shop, Category, Product, ProductInfo,
    Parameter, ProductParameter, Contact, Order, OrderItem, ConfirmEmailToken
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
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
    list_display = ('id', 'name', 'user', 'state')
    list_filter = ('state',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    filter_horizontal = ('shops',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)


class ProductParameterInline(admin.TabularInline):
    model = ProductParameter
    extra = 1


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'shop', 'price', 'quantity')
    list_filter = ('shop',)
    search_fields = ('product__name', 'model')
    inlines = [ProductParameterInline]


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'city', 'street', 'house', 'phone')
    list_filter = ('city',)
    search_fields = ('user__email', 'city', 'phone')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'dt', 'state', 'contact')
    list_filter = ('state',)
    search_fields = ('user__email',)
    inlines = [OrderItemInline]
    readonly_fields = ('dt',)
    list_editable = ('state',)


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'key')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'key')