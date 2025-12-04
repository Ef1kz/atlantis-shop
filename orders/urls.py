# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    path('my/', views.user_orders, name='user_orders'),
]
