from ajax_select import fields
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Product, Category, Order, Basket, User, Review, OrderDetails


class MailingForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={
            'class': 'newsletter_input',
            'required': 'required',
            'type': 'email'
        }
    ))

    class Meta:
        ...


class UserForm(forms.ModelForm):
    """Test modelform to User"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'balance']
        help_texts = {
            'first_name': _('Введите ваше имя')
        }
        labels = {
            'first_name': _('Ваше имя'),
            'last_name': _('Ваша фамилия'),
            'email': _('Ваш email')
        }


class UserOrderForm(forms.ModelForm):
    """
    Форма выбора поля user в модели Order
    """

    class Meta:
        model = Order
        exclude = ('',)

    user = fields.AutoCompleteSelectField('users', label='Клиент')
    product = fields.AutoCompleteSelectMultipleField('products', label='Товар', help_text="""Введите имя товара.""")
    quantity = forms.IntegerField(label='Кол-во товара')

    def __init__(self, *args, **kwargs):
        """dander __init__ redefined for set initial param for attribute quantity"""
        super().__init__(*args, **kwargs)
        instance: Order = kwargs.get('instance')
        if isinstance(instance, self._meta.model):
            self.initial['quantity'] = OrderDetails.objects.filter(
                order_id=instance.pk
            ).only('quantity').order_by().first().quantity


class ReviewDetailForm(forms.ModelForm):
    """
    Форма выбора полей продукта и юзера в модели комментария
    """

    class Meta:
        model = Review
        exclude = ('',)

    user = fields.AutoCompleteSelectField('users', label='Клиент')
    product = fields.AutoCompleteSelectField('products', label='Товар', help_text="""Введите имя товара.""")


class BasketDetailForm(forms.ModelForm):
    """
    Форма выбора полей продукта и юзера в модели корзины
    """

    class Meta:
        model = Basket
        exclude = ('date_hierarchy',)

    user = fields.AutoCompleteSelectField('users', label='Клиент')
    product = fields.AutoCompleteSelectMultipleField('products', label='Товар', help_text="""Введите имя товара.""")


class ProductForm(forms.ModelForm):
    """Модель админки для продуктов"""
    description = forms.CharField(label='Описание', widget=CKEditorUploadingWidget())

    class Meta:
        exclude = ('discontinued',)
        model = Product


class CategoryForm(forms.ModelForm):
    description = forms.CharField(
        label='Описание категории',
        widget=CKEditorUploadingWidget()
    )

    class Meta:
        fields = '__all__'
        model = Category


class QuantityForm(forms.ModelForm):
    quantity = forms.CharField(
        label='Кол-во товара',
        widget=forms.NumberInput(
            attrs={
                'id': 'quantity_input',
                'type': 'text',
                'pattern': '[0-9]*',
                'value': '1'
            }
        )
    )
    # product_id = forms.IntegerField(
    #     label='Айди продукта',
    #     widget=forms.NumberInput(
    #         attrs={
    #             'type': 'hidden'
    #         }
    #     )
    # )

    class Meta:
        model = Basket
        exclude = ('product', 'user', 'added_at')
