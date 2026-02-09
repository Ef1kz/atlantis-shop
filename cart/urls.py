# cart/urls.py
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('count/', views.cart_count, name='cart_count'),
    path('checkout/', views.cart_checkout, name='checkout'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
]