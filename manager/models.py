from django.db import models
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
import json
# Create your models here.
class DeliveryCompany(models.Model):
    company_name = models.CharField(max_length=300)
    city = models.CharField(max_length=300, default="cali")

    def __str__(self) -> str:
        return self.company_name

class Distributor(models.Model):
    full_name = models.CharField(max_length=300)
    delivery_company = models.ForeignKey(DeliveryCompany, on_delete=models.CASCADE)
    telephone = models.CharField(max_length=15, default=0)

    def __str__(self) -> str:
        return self.full_name

class Order(models.Model) :
    email = models.EmailField(verbose_name="CustomerEmail",blank=False, null=False)
    customer_name= models.CharField(max_length=300)
    provider_name= models.CharField(max_length=300, default="")
    city= models.CharField(max_length=100)
    customer_address_2= models.CharField(max_length=100, blank=True)
    customer_address= models.CharField(max_length=50)
    provider_address_2= models.CharField(max_length=100, blank=True)
    provider_address= models.CharField(max_length=50, default="")
    created_at = models.DateTimeField("date created", blank=True, null=True)
    guide =  models.IntegerField(verbose_name="order guide", default=10000000)
    price = models.IntegerField(verbose_name="Pirce", default=0)
    status = models.CharField(max_length=300, default="Pending")
    buyer_platform = models.CharField(max_length=300, default="DROPI")
    delivery_company = models.ForeignKey(DeliveryCompany, on_delete=models.SET_DEFAULT, default=0)
    
    @classmethod
    def to_json(cls):
        data = {
            "email": cls.email,
            "full_name": cls.full_name,
            "city": cls.city,
            "address_2": cls.address_2,
            "address": cls.address,
            "created_at": cls.created_at,  # Convert to ISO 8601 format
            "guide": cls.guide,
            "price": cls.price,
            "status": cls.status,
            "buyer_platform": cls.buyer_platform,
            "delivery_company": cls.delivery_company if cls.delivery_company else None
            # Assuming DeliveryCompany has a 'name' attribute
        }
        return json.dumps(data, cls=DjangoJSONEncoder)

    @classmethod
    def collection_to_json(cls, queryset):
        data = []
        for instance in queryset:
            data.append({
                "email": instance.email,
                "full_name": instance.full_name,
                "city": instance.city,
                "address_2": instance.address_2,
                "address": instance.address,
                "created_at": instance.created_at.isoformat(),
                "guide": instance.guide,
                "price": instance.price,
                "status": instance.status,
                "buyer_platform": instance.buyer_platform,
                "delivery_company": instance.delivery_company.company_name
            })
        return json.dumps(data)    

class Task(models.Model):
    distributor = models.ForeignKey(Distributor, on_delete=models.SET_DEFAULT, default=0)
    order = models.ForeignKey(Order, on_delete=models.SET_DEFAULT, default=0)

class Fee(models.Model):
    city = models.CharField(max_length=30)
    price= models.IntegerField()

    def save(self, *args, **kwargs):
        self.city = self.city.lower()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.city