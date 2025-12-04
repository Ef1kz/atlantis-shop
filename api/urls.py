# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.api_products, name='api_products'),
    path('cart/add/', views.api_cart_add, name='api_cart_add'),
    path('orders/create/', views.api_order_create, name='api_order_create'),
]