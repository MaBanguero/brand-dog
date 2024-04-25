from django.contrib import admin

# Register your models here.

from .models import Order, DeliveryCompany, Task, Distributor, Fee

models = [Order, DeliveryCompany, Task, Distributor, Fee]
admin.site.register(model_or_iterable=models)