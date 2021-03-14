from typing import List, Optional

from ajax_select import register, LookupChannel
from django.db.models import Q
from django.http import HttpRequest

from .models import User, Product


#
# class UserProtocol(Protocol):
#     def get_query(self, q: Optional[str], request: HttpRequest) -> List[User]: ...
#
#     def format_item_display(self, item: User) -> str: ...


@register('users')
class UsersLookup(LookupChannel):
    """
    Lookup для поиска M2M поля в админке(модель User)
    """
    model = User

    def get_query(self, q: Optional[str], request: HttpRequest) -> List[User]:
        # queryset = self.model.objects.prefetch_related(
        #     Prefetch(
        #         'user', queryset=User.objects.filter(first_name__icontains=q), to_attr='user_set'
        #     )
        # ).order_by().only('id')[:50]
        # return [
        #     order.user_set[0]
        #     for order
        #     in queryset if order.user_set != []
        # ]
        return self.model.objects.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )[:50]

    def format_item_display(self, item: User) -> str:
        """
        Вывод в форме найденное значение
        :param item: Object or instance of User
        :return:
        """
        default_representation: str = '#{pk} | {first_name} {last_name}'
        return u"<span class='tag'>%s</span>" % default_representation.format(
            pk=item.pk,
            first_name=item.first_name,
            last_name=item.last_name
        )


@register('products')
class ProductsLookup(LookupChannel):
    model = Product

    def get_query(self, q, request: HttpRequest) -> List[Product]:
        return self.model.objects.filter(
            product_name__icontains=q
        ).all()

    def format_item_display(self, product: Product):
        return u"<span class='tag'>%s</span>" % product
