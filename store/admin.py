from typing import Union, Optional

from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.forms import ModelForm
from django.http import HttpRequest
from django.utils.safestring import mark_safe, SafeString

from .forms import ProductForm, CategoryForm, UserOrderForm, ReviewDetailForm, BasketDetailForm
from .models import Product, Category, Order, User, OrderDetails, Review, Basket


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Класс продукта для админки
    """
    list_display = (
        'product_name', 'unit_price', 'category', 'created_at', 'description', 'quantity', 'check_discontinued',
        'get_image', 'slug'
    )
    list_filter = ('created_at', 'color', 'category')
    search_fields = ('category__name',)
    list_display_links = ('product_name',)
    readonly_fields = ('get_image', 'check_discontinued')
    save_on_top = True
    form = ProductForm
    save_as = True
    date_hierarchy = 'created_at'

    def check_discontinued(self, obj: Product) -> bool:
        return obj.quantity <= 0

    @staticmethod
    def get_image(obj: Product) -> Union[SafeString, str]:
        if obj.photo:
            return mark_safe(f'<img src={obj.photo.url} width="80" height="65">')
        else:
            return 'Фото не установлено!'

    get_image.short_description = 'Фотография товара'
    check_discontinued.short_description = 'Закончился ли товар'
    check_discontinued.boolean = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Класс категории для админки
    """
    list_display = ('name', 'get_image', 'slug')
    readonly_fields = ('get_image',)
    search_fields = ('name',)
    form = CategoryForm
    save_on_top = True
    save_as = True

    @staticmethod
    def get_image(obj: Category) -> SafeString:
        return mark_safe(f'<img src="{obj.photo.url}" width="250" height="150">')

    get_image.short_description = 'Фото'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'balance')
    list_filter = ('balance',)
    list_display_links = ('first_name', 'last_name', 'email')


class OrderDetailsInline(admin.TabularInline):
    model = OrderDetails
    fields = ('quantity',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_select_related = ('user',)
    list_display = (
        'unique_abbreviation', 'discount', 'canceled', 'order_date', 'get_order_sum', 'user'
    )
    form = UserOrderForm
    list_filter = ('order_date', 'unique_abbreviation')
    list_display_links = ('unique_abbreviation',)
    empty_value_display = 'unknown'
    search_fields = ('product__category__name',)
    readonly_fields = ('get_order_sum', 'order_date')
    list_per_page = 50

    def get_quantity(self, order: Order):
        return OrderDetails.objects.filter(
            order_id=order.pk
        ).only('quantity').order_by().first().quantity

    def get_unit_price(self, order: Order):
        return OrderDetails.objects.filter(
            order_id=order.pk
        ).only('unit_price').order_by().first().unit_price

    def save_model(self, request: HttpRequest, obj: Order, form: ModelForm, change):
        super().save_model(request, obj, form, change)
        Order.objects.filter(
            pk=obj.pk
        ).update(
            discount=True
        )
        product_id = form.cleaned_data.get('product')[0]
        OrderDetails.objects.filter(
            product_id=int(product_id)
        ).update(
            unit_price=Product.objects.filter(pk=int(product_id)).values_list('unit_price', flat=True)[0],
            quantity=form.cleaned_data.get('quantity')
        )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_form(self, request: WSGIRequest, obj: Union[Order, None] = None, **kwargs):
        return super().get_form(request, obj, **kwargs)

    get_quantity.short_description = 'Кол-во товара'
    get_unit_price.short_description = 'Цена за штуку'
    Order.get_order_sum.short_description = 'Общая сумма заказа'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_select_related = ('user', 'product')
    list_display = ('body', 'product', 'user', 'is_active', 'created_at')
    list_filter = ('created_at',)
    list_per_page = 40
    search_fields = ('product__name',)
    form = ReviewDetailForm

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_form(self, request: WSGIRequest, obj: Optional[Order] = None, **kwargs):
        return super().get_form(request, obj, **kwargs)


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at',)
    list_filter = ('added_at',)
    date_hierarchy = 'added_at'
    list_per_page = 40
    search_fields = ('user__first_name', 'product__product_name')
    form = BasketDetailForm
    empty_value_display = 'unknown'
    save_as = True

    def get_form(self, *args, **kwargs):
        return super().get_form(*args, **kwargs)

    def formfield_for_foreignkey(self, db_field, request: WSGIRequest, **kwargs):
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.site_title = 'GLEF1X SHOP'
admin.site.site_header = 'GLEF1X SHOP'
