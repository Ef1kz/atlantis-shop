# products/urls.py
from django.urls import path
from . import views

app_name = 'products'
urlpatterns = [
    path('', views.product_list, name='product_list'),
    # Сначала — конкретный товар по ID (число)
    path('<int:pk>/', views.product_detail, name='product_detail'),
    # Потом — категории по slug (только если не число)
    path('<slug:collection_slug>/', views.product_list_by_collection, name='product_list_by_collection'),
]