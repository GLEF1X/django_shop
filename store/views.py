from datetime import date
from typing import Dict, Any, List, Union

from django import http
from django.core.mail import send_mail
from django.db.models import Prefetch, Sum, F, DecimalField, QuerySet
from django.forms import model_to_dict
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, FileResponse, HttpResponseRedirect, \
    JsonResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.template.response import SimpleTemplateResponse
from django.urls import reverse_lazy, reverse, resolve
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.defaults import page_not_found

from store.forms import MailingForm, UserForm, QuantityForm
from store.models import Order, Product, Category, Review, Basket


# def show_index(request: HttpRequest) -> HttpResponse:
#     return render(request=request, template_name='store/index.html')

class FilledListView(generic.ListView):
    """ListView with some base params in context data"""

    def get_context_data(self, *args, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(*args, **kwargs)
        context['basket_item_count'] = Basket.objects.count()
        return context


class FilledDetailView(generic.DetailView):
    """DetailView with some base params in context data"""

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['basket_item_count'] = Basket.objects.count()
        return context


def index(request: HttpRequest) -> HttpResponse:
    # order = Order.objects.select_related('user') \
    #     .values('user__first_name', 'user__last_name', 'unit_price', 'quantity',
    #             order_price=
    #             Sum(F('unit_price') * F('quantity'),
    #                 output_field=DecimalField())
    #             ) \
    #     .all()
    # queryset = Order.objects.filter(unit_price__gte=10).only('unit_price', 'discount', 'quantity').all()
    # prefetch = Prefetch('order_set', queryset=queryset,
    #                     to_attr='orders')
    # orders = User.objects.prefetch_related(
    #     prefetch
    # ).only('first_name', 'last_name').all()
    # orders = Order.objects.only('unit_price', 'discount', 'quantity', 'user__first_name', 'user__last_name',
    #                             'order_date').first()
    # print(orders.user)

    queryset = Order.entries.filter(unit_price__gte=10).only(
        'unit_price', 'discount', 'quantity', 'order_date',
        'user_id'
    ).all()
    prefetch = Prefetch('order_set', queryset=queryset, to_attr='orders')
    # user = User.objects.prefetch_related(
    #     prefetch
    # ).only('first_name', 'last_name').all()
    order_price = Sum(
        F('unit_price') * F('quantity'), output_field=DecimalField()
    )
    # orders = list(
    #     Order.entries.filter(
    #         unit_price__range=(10, 254)).only(
    #         'quantity', 'unit_price', 'discount', 'order_date', 'unique_abbreviation', 'product_id', 'canceled'
    #     ).annotate(order_price=order_price).all().prefetch_related(
    #         Prefetch('user', queryset=User.objects.only('first_name', 'last_name'), to_attr='users'),
    #         Prefetch('product', queryset=Product.objects.only('photo', 'size', 'created_at'), to_attr='products')
    #     )
    # )
    # return HttpResponse(content='Hello world!')
    orders = []
    return render(
        request=request,
        template_name='order_list.html',
        context={
            'orders': orders
        }
    )


class ProductListView(FilledListView):
    order_price = Sum(
        F('unit_price') * F('quantity'), output_field=DecimalField()
    )
    model = Product
    # queryset = list(
    #     Order.entries.prefetch_related(
    #         Prefetch('user', queryset=User.objects.only('first_name', 'last_name'), to_attr='users'),
    #         Prefetch('product',
    #                  queryset=Product.objects.only('photo', 'size', 'created_at', 'quantity', 'unit_price').annotate(
    #                      order_price=order_price),
    #                  to_attr='products')
    #     ).filter(
    #         unit_price__range=(10, 254)).only(
    #         'product', 'discount', 'order_date', 'unique_abbreviation', 'product', 'canceled'
    #     ).all()
    # )
    template_name = 'store/product_list.html'
    context_object_name = 'product_list'

    def get_context_data(self, *args, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(*args, **kwargs)
        context['all_categories'] = Category.objects.distinct().only('slug', 'name').all()
        context['mailing_form'] = MailingForm()
        context['count'] = Basket.objects.count()
        # products = list(Product.objects.all().order_by().only('unit_price', 'product_name', 'photo'))
        # context['product_list'] = products
        return context

    def get_queryset(self) -> Any:
        return self.model.objects.only(
            'unit_price', 'product_name', 'photo', 'slug'
        ).order_by()


class CategoriesView(FilledDetailView):
    model = Category
    template_name = 'store/category_detail.html'
    context_object_name = 'category'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        category = self.get_object(super().get_queryset())
        context['products'] = Product.objects.filter(
            category_id=category.pk
        ).only(
            'slug', 'unit_price', 'product_name', 'description', 'quantity', 'discontinued', 'photo', 'slug'
        ).all()
        return context

    def get_queryset(self) -> QuerySet[Category]:
        return Category.objects.distinct().only(
            'slug', 'name', 'photo', 'description'
        ).order_by()


class ProductDetailView(FilledDetailView):
    model = Product
    template_name = 'store/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self) -> QuerySet[Product]:
        return Product.objects.filter(discontinued=False).prefetch_related(
            Prefetch('category', queryset=Category.objects.only('name', 'description', 'id'), to_attr='s_category')
        ).only(
            'slug', 'unit_price', 'product_name', 'description', 'quantity', 'discontinued', 'photo', 'slug',
            'category_id'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_categories'] = Category.objects.prefetch_related(
            Prefetch('comments', queryset=Review.objects.only('id'), to_attr='comments')
        ).only('slug', 'name').all()
        context['reviews'] = Product.objects.filter(
            slug=self.kwargs['slug']
        ).first()
        context['mailing_form'] = MailingForm()
        context['quantity_input'] = QuantityForm()
        return context
    # slug_url_kwarg = 'slug'


class UserTemplateResponse(SimpleTemplateResponse):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def resolve_context(self, context: dict) -> dict:
        context['date'] = date.today()
        return context


def today_view(request: HttpRequest) -> HttpResponseNotFound:
    template = UserTemplateResponse(
        template='404.html',
        context={

        }
    )
    rendered = template.render()
    return rendered


def month_view(request: HttpRequest, pk: int):
    return HttpResponse('HELLO WORLD')


def not_found_view(request: HttpRequest):
    return page_not_found(
        request=request, template_name='404.html'
    )


class MailingView(generic.View):
    """View for mailing users"""

    def post(self, request: HttpRequest) -> HttpResponse:
        form = MailingForm(data=request.POST)
        new_form = MailingForm()
        products: Union[List[Category], List[None]] = []
        categories: Union[List[Category], List[None]] = []
        sent = False
        if form.is_valid():
            send_mail(
                subject='Подписка на сайте!',
                message="""Здравствуйте, ваша подписка была успешно оформлена и принята в обработку,
теперь ежедневно вы будете получать нашу рассылку""",
                from_email='glebgar567@gmail.com',
                recipient_list=[form.cleaned_data['email']]
            )
            sent = True
            categories = Category.objects.distinct().only('slug', 'name').all()
            products = Product.objects.only(
                'unit_price', 'product_name', 'photo', 'slug'
            ).distinct().order_by()
        return render(
            request=request,
            template_name='store/product_list.html',
            status=200,
            context={
                'mailing_form': new_form,
                'sent': sent,
                'all_categories': categories,
                'product_list': products
            }
        )


class FormView(generic.FormView):
    form_class = UserForm
    template_name = 'store/form_test.html'

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = UserForm(
            label_suffix=' =>'
        )
        return context

    def get_success_url(self) -> Any:
        return reverse_lazy('store:index')


class ValidateView(generic.View):

    def post(self, request: HttpRequest) -> http:
        form = UserForm(request.POST)
        # print(request.get_signed_cookie(
        #     'csrf_token', default={
        #         'csrf_token': 'unknown'
        #     }
        # ))
        # q = QueryDict(
        #     query_string='a=1&a=2&a=3'
        # )
        # print(q.__contains__(
        #     'a'
        # ))
        # q._mutable = True
        # print(request.get_raw_uri())
        # print(request.META)
        if form.is_valid():
            form.save()
            return redirect(
                reverse_lazy('store:index')
            )
        return HttpResponse(status=400)


def base_view(request: HttpRequest) -> FileResponse:
    # response = HttpResponse()
    # response['Age'] = 120
    # response.set_cookie(
    #     key='Value',
    #     value='cringe123',
    #     max_age=60
    # )
    # return response
    # response = FileResponse(
    #     open('/home/gleb/python_projects/djangoProject/static/images/check.png', 'rb'),
    #     as_attachment=True
    # )
    # response['Age'] = 120  # response.__setitem__('Age', 120)
    # response.set_cookie(
    #     key='Value',
    #     value='cringe123',
    #     max_age=60,
    #     secure=True
    # )
    # return response
    ...


class BasketView(FilledListView):
    template_name = 'store/cart.html'
    model = Basket
    context_object_name = 'basket'

    def get_queryset(self):
        columns = ("unit_price", "product_name", "photo", "slug")
        return self.model.objects.prefetch_related(
            Prefetch('product', queryset=Product.objects.order_by().only(*columns), to_attr="products")
        ).order_by().only("product_id", "quantity").all()

    def get_context_data(self, **kwargs):
        annotation = Sum(F('product__unit_price') * F('quantity'), output_field=DecimalField())
        context = super().get_context_data(**kwargs)
        context['detail'] = self.model.objects.filter(user_id=1).aggregate(cart_details=annotation).get('cart_details')
        return context


class FillBasket(generic.View):

    def post(self, request: HttpRequest) -> HttpResponseRedirect:
        form = QuantityForm(request.POST)
        if form.is_valid():
            product_id = request.POST.get(key='product_id', default=None)
            Basket(user_id=1, product_id=product_id, quantity=form.cleaned_data.get('quantity')).save()
            return HttpResponseRedirect(
                reverse_lazy('store:basket')
            )


class UpdateBasket(generic.View):
    def get(self, request: HttpRequest) -> HttpResponseRedirect:
        """Do some staff with cart(delete items)"""
        match = resolve(request.path)
        if match.view_name == f'{match.app_name}:clear_cart':
            Basket.objects.filter(user_id=1).delete()
            return redirect(
                to=reverse('store:basket')
            )
        else:
            print("UPDATING")


class ApiView(generic.View):

    def post(self, request: HttpRequest) -> Union[JsonResponse, HttpResponseNotAllowed]:
        from djangoProject.settings import SECRET_KEY, SECRET_CODE
        if request.POST['SECRET_KEY'] == SECRET_KEY:
            if request.POST['SECRET_CODE'] == SECRET_CODE:
                return JsonResponse(
                    data=model_to_dict(Review.objects.filter(pk=1).first()), safe=False
                )
        return HttpResponseNotAllowed(
            permitted_methods='GET'
        )

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ApiView, self).dispatch(request, *args, **kwargs)


class BaseView2(generic.View):
    def get(self, *args, **kwargs) -> HttpResponseRedirect:
        pass
