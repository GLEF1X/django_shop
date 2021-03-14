from datetime import date
from enum import unique
from functools import cached_property
from typing import Union, List, Optional

from django.db import models
from django.db.models import Sum, F, DecimalField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from store.utils import managers
from store.utils.values_worker import generate_abbreviation, format_saving_kwargs


class Category(models.Model):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    name = models.CharField(max_length=150, verbose_name='Название категории', db_index=True)
    slug = models.SlugField(max_length=70, default='0')
    photo = models.ImageField(
        upload_to='product/categories/', verbose_name='Фотография категории', null=True,
        db_index=True
    )
    discount = models.IntegerField(
        verbose_name='Скидка на товар', db_index=True, default=0
    )
    description = models.TextField(verbose_name='Описание товара', default=None, db_index=True, null=True)

    def save(self, *args, **kwargs):
        self.slug = self.name if self.slug == '0' else self.slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f'# {self.pk} | {self.name}'

    def get_absolute_url(self) -> Optional[str]:
        from django.urls import reverse
        return reverse(
            viewname='store:category-detail',
            kwargs={
                'slug': self.slug
            }
        )


class Product(models.Model):
    """Product model"""

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['created_at']

    @unique
    class ProductSizes(models.TextChoices):
        SMALL = 'RED', _('Красный')
        MEDIUM = 'BLACK', _('Черный')
        LARGE = 'WHITE', _('Белый')
        CUSTOM = 'C', _('Пользовательский')

    # Bad Practice
    # PRODUCT_SIZES = (
    #     ('S', 'Small'),
    #     ('M', 'Medium'),
    #     ('L', 'Large'),
    #     ('None', 'Custom')
    # )
    product_name = models.CharField(max_length=200, blank=False, verbose_name='Наименование продукта')
    color = models.CharField(
        max_length=30,
        blank=False,
        verbose_name='Цвет товара',
        choices=ProductSizes.choices,
        default=ProductSizes.CUSTOM
    )
    unit_price = models.DecimalField(max_digits=12, verbose_name='Цена товара', decimal_places=2, default=0)
    created_at = models.DateField(verbose_name='Время создания', default=date.today, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(verbose_name='Описание товара', default=None, db_index=True, null=True)
    quantity = models.SmallIntegerField(verbose_name='Кол-во товара(на складе)', default=0)
    discontinued = models.BooleanField(default=False, verbose_name='Закончился ли товар?')
    slug = models.SlugField(
        max_length=8, verbose_name='Уникальный идентификатор продукта',
        default=generate_abbreviation
    )
    photo = models.ImageField(
        upload_to='product/product_photos/%Y/%m/%d', verbose_name='Фотография товара',
        default=None,
        null=True,
        db_index=True
    )
    category = models.ForeignKey(
        related_name='categories',
        to=Category,
        verbose_name='Номер категории',
        on_delete=models.SET_NULL,
        null=True,
    )

    def save(self, *args, **kwargs):
        self.created_at = timezone.now()
        if not self.description:
            self.description = f'Товар #{self.pk} {self.product_name}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.pk} | {self.product_name}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse(
            'store:product-detail', kwargs={
                'slug': self.slug
            }
        )


class User(models.Model):
    """Simple User model, custom indexes on first_name and last_name"""

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        indexes = [
            models.Index(fields=['first_name', 'last_name'])
        ]

    prepopulated_fields = {'slug': ("user_id",)}
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(verbose_name='Имя пользователя', max_length=200)
    last_name = models.CharField(verbose_name='Фамилия пользователя', max_length=200)
    email = models.EmailField(max_length=200, verbose_name='Email пользователя', unique=True, db_index=True)
    balance = models.DecimalField(max_digits=12, verbose_name='Баланс пользователя', decimal_places=2, default=0)

    def __str__(self):
        return f"#{self.user_id} | {self.first_name} {self.last_name}"


class OrderDetails(models.Model):
    """M2M table through Product and Order models, have additional information about order"""
    order = models.ForeignKey('Order', on_delete=models.CASCADE, db_index=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, db_index=True)

    class Meta:
        db_table = 'news_order_details'

    unit_price = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        verbose_name='Цена за штуку',
        default=1
    )
    quantity = models.SmallIntegerField(verbose_name='Кол-во товаров в чеке', default=1)

    def save(self, *args, **kwargs):
        queryset = Product.objects.filter(pk=self.order_id).only('unit_price', 'quantity').order_by().first()
        self.unit_price = queryset.unit_price
        self.quantity = queryset.quantity
        super().save(*args, **kwargs)


class Order(models.Model):
    """Модель заказа"""
    objects = models.Manager()
    entries = managers.OrderManager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['order_date']
        get_latest_by = ['order_date']

    order_date = models.DateField(auto_now_add=True, verbose_name='Время заказа', db_index=True)
    user = models.ForeignKey(User, verbose_name='Юзер, который сделал заказ', on_delete=models.SET_DEFAULT, default=0)
    product = models.ManyToManyField(
        Product, through=OrderDetails, through_fields=(
            'order', 'product'
        ))
    canceled = models.BooleanField(verbose_name='Продан ли товар', default=False)
    discount = models.SmallIntegerField(verbose_name='Бонус при покупке', default=0)
    unique_abbreviation = models.SlugField(max_length=8, verbose_name='Уникальный номер заказа',
                                           default=generate_abbreviation)

    @cached_property
    def get_order_sum(self) -> Union[List[float], str]:
        """
        Function to get order sum price, calculating as unit_price * quantity

        :return: float or 'unknown'
        """
        order_price = Sum(
            F('unit_price') * F('quantity'), output_field=DecimalField()
        )
        details = OrderDetails.objects.filter(
            order_id=self.pk).only('unit_price', 'quantity').annotate(
            order_price=order_price
        ).all()
        try:
            return [float(obj.order_price) for obj in details]
        except KeyError:
            return 'unknown'
        except TypeError:
            return 'unknown'

    @classmethod
    def instance(cls, **kwargs):
        """Get instance of class"""
        return cls(**kwargs)

    def save_(self, *args, **kwargs) -> None:
        """Custom save method, adding related objects into db"""
        product_id = kwargs.get("product_id")
        self.unique_abbreviation = generate_abbreviation()
        self.order_date = timezone.now().date()
        formatted_kwargs, initializer_kwargs = format_saving_kwargs(
            kwargs=kwargs,
            attrs=[
                'product', 'product_id', 'discount', 'quantity'
            ]

        )
        self.unit_price = Product.objects.filter(id=product_id).values('unit_price')
        _instance = self.instance(
            unique_abbreviation=self.unique_abbreviation,
            order_date=self.order_date,
            unit_price=self.unit_price,
            user=User.objects.filter(pk=kwargs.get('user_id')).first(),
            **formatted_kwargs
        )
        _instance.save(*args, **initializer_kwargs)

    @staticmethod
    def get_absolute_url() -> str:
        from django.urls import reverse
        return reverse(
            'store:order_detail'
        )

    def __str__(self):
        return f'#{self.pk} | {self.order_date}'


class Review(models.Model):
    """Model of review"""

    objects = models.Manager()  # Base manager
    active = managers.Active()  # manager, which create query only for reviews with is_active = True

    class Meta:
        ordering = ['created_at']
        get_latest_by = ['created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Коментарии'
        indexes = [
            models.Index(
                fields=('body',)
            )
        ]

    body = models.TextField(verbose_name='Текст комментария')
    product = models.ForeignKey(
        to=Product,
        on_delete=models.PROTECT,
        related_name='comments'
    )
    user = models.ForeignKey(
        to=User,
        verbose_name='Пользователь, который оставил комментарий',
        related_name='comments',
        on_delete=models.PROTECT
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен ли комментарий')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return '{} to {} comment'.format(self.user, self.product)


class TimeBasedModel(models.Model):
    class Meta:
        abstract = True

    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Когда добавлен')


class Basket(TimeBasedModel):
    user = models.ForeignKey(
        verbose_name='Пользователь',
        db_index=True,
        related_name='users',
        to=User,
        on_delete=models.PROTECT
    )
    product = models.ForeignKey(
        verbose_name='Продукт, который был занесён в корзину',
        related_name='products',
        db_index=True,
        to=Product,
        on_delete=models.PROTECT
    )
    quantity = models.SmallIntegerField(verbose_name='Кол-во товара в корзине', default=1)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Корзина'

    def __str__(self):
        """String representation of basket object"""
        return """{} added to basket {}""".format(self.user, self.product)
