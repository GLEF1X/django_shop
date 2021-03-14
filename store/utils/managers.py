from typing import Any

from django.db import models


class OrderManager(models.Manager):
    def get_queryset(self) -> Any:
        return super(OrderManager, self).get_queryset().filter(canceled=False).order_by()


class Active(models.Manager):
    def get_queryset(self) -> Any:
        return super(Active, self).get_queryset().filter(active=True).order_by()
