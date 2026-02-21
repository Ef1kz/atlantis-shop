from django.urls import path
from . import views  # ← Это импортирует views из cart/views.py

app_name = 'cart'

urlpatterns = [
    path('add/<int:product_id>/', views.add, name='add'),
    path('count/', views.count, name='count'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('', views.detail, name='detail'),
    path('remove/<int:item_id>/', views.remove, name='remove'),  # ← Здесь views определено
]