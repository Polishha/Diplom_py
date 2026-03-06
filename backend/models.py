"""
Модели данных для приложения автоматизации закупок.
Содержит все модели: пользователи, магазины, товары, заказы и т.д.
"""

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.tokens import get_token_generator

# Константы для выбора статусов
STATE_CHOICES = (
    ('basket', 'Корзина'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),
)


class UserManager(BaseUserManager):
    """
    Менеджер для создания пользователей.
    
    Расширяет стандартный BaseUserManager для работы с email в качестве
    основного идентификатора вместо username.
    
    Methods:
        _create_user: Внутренний метод для создания пользователя
        create_user: Создание обычного пользователя
        create_superuser: Создание суперпользователя
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Внутренний метод для создания и сохранения пользователя.
        
        Args:
            email (str): Email пользователя
            password (str): Пароль пользователя
            **extra_fields: Дополнительные поля модели User
            
        Returns:
            User: Созданный пользователь
            
        Raises:
            ValueError: Если email не указан
        """
        if not email:
            raise ValueError('Email должен быть указан')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Создание обычного пользователя.
        
        Args:
            email (str): Email пользователя
            password (str, optional): Пароль пользователя
            **extra_fields: Дополнительные поля
            
        Returns:
            User: Созданный пользователь
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Создание суперпользователя с правами администратора.
        
        Args:
            email (str): Email суперпользователя
            password (str): Пароль суперпользователя
            **extra_fields: Дополнительные поля
            
        Returns:
            User: Созданный суперпользователь
            
        Raises:
            ValueError: Если не установлены права is_staff или is_superuser
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Расширенная модель пользователя.
    
    Заменяет стандартную модель Django User, используя email в качестве
    основного идентификатора вместо username. Добавляет поля для типа
    пользователя (покупатель/магазин) и дополнительной информации.
    
    Attributes:
        email (EmailField): Email пользователя (уникальный)
        company (CharField): Название компании (для поставщиков)
        position (CharField): Должность в компании
        type (CharField): Тип пользователя: 'buyer' или 'shop'
        first_name (CharField): Имя
        last_name (CharField): Фамилия
        patronymic (CharField): Отчество
        is_active (BooleanField): Активен ли пользователь (подтвержден email)
    """
    REQUIRED_FIELDS = []
    objects = UserManager()
    USERNAME_FIELD = 'email'
    
    email = models.EmailField(_('email address'), unique=True)
    company = models.CharField(verbose_name='Компания', max_length=40, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True)
    
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    
    type = models.CharField(
        verbose_name='Тип пользователя', 
        choices=USER_TYPE_CHOICES, 
        max_length=5, 
        default='buyer'
    )
    
    first_name = models.CharField(verbose_name='Имя', max_length=30, blank=True)
    last_name = models.CharField(verbose_name='Фамилия', max_length=30, blank=True)
    patronymic = models.CharField(verbose_name='Отчество', max_length=30, blank=True)

    def __str__(self):
        """
        Строковое представление пользователя.
        
        Returns:
            str: Имя и фамилия или email, если имя не указано
        """
        return f'{self.first_name} {self.last_name}'.strip() or self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('email',)


class Shop(models.Model):
    """
    Модель магазина (поставщика).
    
    Содержит информацию о магазине, его владельце и статусе приема заказов.
    
    Attributes:
        name (CharField): Название магазина
        url (URLField): Ссылка на прайс-лист (YAML)
        user (OneToOneField): Пользователь-владелец магазина (тип 'shop')
        state (BooleanField): Статус приема заказов (True - принимает)
    """
    name = models.CharField(max_length=50, verbose_name='Название')
    url = models.URLField(verbose_name='Ссылка', null=True, blank=True)
    user = models.OneToOneField(
        User, 
        verbose_name='Пользователь',
        blank=True, 
        null=True,
        on_delete=models.CASCADE,
        limit_choices_to={'type': 'shop'}
    )
    state = models.BooleanField(verbose_name='Статус получения заказов', default=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"
        ordering = ('-name',)

    def __str__(self):
        """
        Строковое представление магазина.
        
        Returns:
            str: Название магазина
        """
        return self.name


class Category(models.Model):
    """
    Модель категории товаров.
    
    Категории могут быть связаны с несколькими магазинами.
    
    Attributes:
        name (CharField): Название категории
        shops (ManyToManyField): Магазины, в которых есть товары этой категории
    """
    name = models.CharField(max_length=40, verbose_name='Название')
    shops = models.ManyToManyField(
        Shop, 
        verbose_name='Магазины', 
        related_name='categories', 
        blank=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = "Список категорий"
        ordering = ('-name',)

    def __str__(self):
        """
        Строковое представление категории.
        
        Returns:
            str: Название категории
        """
        return self.name


class Product(models.Model):
    """
    Модель товара (без привязки к магазину).
    
    Содержит базовую информацию о товаре, общую для всех магазинов.
    
    Attributes:
        name (CharField): Название товара
        category (ForeignKey): Категория товара
    """
    name = models.CharField(max_length=80, verbose_name='Название')
    category = models.ForeignKey(
        Category, 
        verbose_name='Категория', 
        related_name='products', 
        blank=True,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"
        ordering = ('-name',)

    def __str__(self):
        """
        Строковое представление товара.
        
        Returns:
            str: Название товара
        """
        return self.name


class ProductInfo(models.Model):
    """
    Информация о товаре в конкретном магазине.
    
    Связывает товар с магазином и содержит цену, количество и другие
    специфичные для магазина данные.
    
    Attributes:
        model (CharField): Модель товара
        external_id (PositiveIntegerField): ID товара в системе поставщика
        product (ForeignKey): Ссылка на товар
        shop (ForeignKey): Ссылка на магазин
        quantity (PositiveIntegerField): Количество на складе
        price (PositiveIntegerField): Цена
        price_rrc (PositiveIntegerField): Рекомендуемая розничная цена
    """
    model = models.CharField(max_length=80, verbose_name='Модель', blank=True)
    external_id = models.PositiveIntegerField(verbose_name='Внешний ИД')
    product = models.ForeignKey(
        Product, 
        verbose_name='Продукт', 
        related_name='product_infos', 
        blank=True,
        on_delete=models.CASCADE
    )
    shop = models.ForeignKey(
        Shop, 
        verbose_name='Магазин', 
        related_name='product_infos', 
        blank=True,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = "Информационный список о продуктах"
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'shop', 'external_id'], 
                name='unique_product_info'
            ),
        ]

    def __str__(self):
        """
        Строковое представление информации о товаре.
        
        Returns:
            str: Название товара и магазина
        """
        return f"{self.product.name} - {self.shop.name}"


class Parameter(models.Model):
    """
    Модель параметра товара (характеристики).
    
    Например: "Цвет", "Вес", "Материал" и т.д.
    
    Attributes:
        name (CharField): Название параметра
    """
    name = models.CharField(max_length=40, verbose_name='Название')

    class Meta:
        verbose_name = 'Имя параметра'
        verbose_name_plural = "Список имен параметров"
        ordering = ('-name',)

    def __str__(self):
        """
        Строковое представление параметра.
        
        Returns:
            str: Название параметра
        """
        return self.name


class ProductParameter(models.Model):
    """
    Значение параметра для конкретного товара в магазине.
    
    Связывает товар с параметром и хранит его значение.
    
    Attributes:
        product_info (ForeignKey): Информация о товаре
        parameter (ForeignKey): Параметр
        value (CharField): Значение параметра
    """
    product_info = models.ForeignKey(
        ProductInfo, 
        verbose_name='Информация о продукте',
        related_name='product_parameters', 
        blank=True,
        on_delete=models.CASCADE
    )
    parameter = models.ForeignKey(
        Parameter, 
        verbose_name='Параметр', 
        related_name='product_parameters', 
        blank=True,
        on_delete=models.CASCADE
    )
    value = models.CharField(verbose_name='Значение', max_length=100)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"
        constraints = [
            models.UniqueConstraint(
                fields=['product_info', 'parameter'], 
                name='unique_product_parameter'
            ),
        ]

    def __str__(self):
        """
        Строковое представление параметра товара.
        
        Returns:
            str: Параметр и его значение
        """
        return f"{self.parameter.name}: {self.value}"


class Contact(models.Model):
    """
    Контактная информация пользователя (адрес доставки).
    
    Attributes:
        user (ForeignKey): Пользователь
        city (CharField): Город
        street (CharField): Улица
        house (CharField): Дом
        structure (CharField): Корпус
        building (CharField): Строение
        apartment (CharField): Квартира
        phone (CharField): Телефон
    """
    user = models.ForeignKey(
        User, 
        verbose_name='Пользователь',
        related_name='contacts', 
        blank=True,
        on_delete=models.CASCADE
    )

    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        """
        Строковое представление контакта.
        
        Returns:
            str: Адрес в формате "Город, улица, дом"
        """
        return f'{self.city}, {self.street}, {self.house}'


class Order(models.Model):
    """
    Модель заказа.
    
    Содержит информацию о заказе пользователя: дату создания, статус,
    контактную информацию и связь с позициями заказа.
    
    Attributes:
        user (ForeignKey): Пользователь, создавший заказ
        dt (DateTimeField): Дата и время создания заказа
        state (CharField): Текущий статус заказа
        contact (ForeignKey): Контактная информация для доставки
    
    Status choices:
        - basket: Корзина (не оформленный заказ)
        - new: Новый заказ
        - confirmed: Подтвержден
        - assembled: Собран
        - sent: Отправлен
        - delivered: Доставлен
        - canceled: Отменен
    """
    user = models.ForeignKey(
        User, 
        verbose_name='Пользователь',
        related_name='orders', 
        blank=True,
        on_delete=models.CASCADE
    )
    dt = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время')
    state = models.CharField(verbose_name='Статус', choices=STATE_CHOICES, max_length=15)
    contact = models.ForeignKey(
        Contact, 
        verbose_name='Контакт',
        blank=True, 
        null=True,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказов"
        ordering = ('-dt',)

    def __str__(self):
        """
        Строковое представление заказа.
        
        Returns:
            str: Номер заказа и дата создания
        """
        return f"Заказ №{self.id} от {self.dt.strftime('%d.%m.%Y %H:%M')}"
    
    @property
    def total_price(self):
        """
        Вычисление общей суммы заказа.
        
        Returns:
            int: Сумма всех позиций заказа
        """
        return sum(item.quantity * item.product_info.price for item in self.ordered_items.all())


class OrderItem(models.Model):
    """
    Позиция в заказе.
    
    Связывает заказ с конкретным товаром из магазина и указывает количество.
    
    Attributes:
        order (ForeignKey): Заказ
        product_info (ForeignKey): Информация о товаре
        quantity (PositiveIntegerField): Количество товара
    """
    order = models.ForeignKey(
        Order, 
        verbose_name='Заказ', 
        related_name='ordered_items', 
        blank=True,
        on_delete=models.CASCADE
    )
    product_info = models.ForeignKey(
        ProductInfo, 
        verbose_name='Информация о продукте', 
        related_name='ordered_items',
        blank=True,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = "Список заказанных позиций"
        constraints = [
            models.UniqueConstraint(
                fields=['order_id', 'product_info'], 
                name='unique_order_item'
            ),
        ]

    def __str__(self):
        """
        Строковое представление позиции заказа.
        
        Returns:
            str: Название товара и количество
        """
        return f"{self.product_info.product.name} x {self.quantity}"


class ConfirmEmailToken(models.Model):
    """
    Токен для подтверждения email при регистрации.
    
    Генерируется при регистрации и отправляется пользователю на email.
    После подтверждения удаляется.
    
    Attributes:
        user (ForeignKey): Пользователь
        created_at (DateTimeField): Дата создания токена
        key (CharField): Уникальный ключ токена
    """
    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        """
        Генерация случайного токена.
        
        Returns:
            str: Случайный токен
        """
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    key = models.CharField(
        "Ключ",
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        """
        Сохранение токена с автоматической генерацией ключа.
        
        Если ключ не указан, генерирует новый перед сохранением.
        """
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        """
        Строковое представление токена.
        
        Returns:
            str: Описание токена с email пользователя
        """
        return f"Токен подтверждения для {self.user.email}"