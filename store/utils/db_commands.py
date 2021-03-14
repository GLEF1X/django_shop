from asgiref.sync import sync_to_async
from django.db.models import Sum, F, DecimalField

from store.models import Order


@sync_to_async
def first_command():
    return Order.objects.select_related('user') \
        .values('user__first_name', 'user__last_name', 'unit_price', 'quantity',
                order_price=
                Sum(F('unit_price') * F('quantity'),
                    output_field=DecimalField())
                ) \
        .all()
