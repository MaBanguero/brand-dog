from django.urls import path
from . import views

app_name = "manager"

urlpatterns = [
    path("V1/publish_order", views.newOrder, name="newOrder"),
    path("V1/distributor/assign", views.assignDistributor, name="assignDistributor"),
    path("V1/distributor/<int:company_id>", views.getDistributor, name="getDistributor"),
    path("V1/distributor/create", views.createDistributor, name="createDistributor"),
    path("V1/orders/<int:order_id>", views.getOrder, name="getOrders"),
    path("V1/orders/", views.getOrder, name="getOrder"),
    path("V1/orders/update", views.updateOrder, name="updateOrder"),
    path('V1/user/create', views.register, name="register"),
    path('V1/user/login', views.login, name="login"),
    path('V1/deliverycompany/create', views.createDeliveryCompany, name="createDeliveryCompany"),
    path('V1/deliverycompany/<int:delivery_company_id>', views.getDeliveryCompany, name="getDeliveryCompany"),

]