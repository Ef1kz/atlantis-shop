# debug_admin.py
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atlantis.settings')
django.setup()

from django.contrib import admin
from django.contrib.admin.sites import site

print("=== ПРОВЕРКА АДМИНКИ ===")
print(f"Всего зарегистрировано моделей: {len(site._registry)}")

# Проверим конкретные модели
try:
    from products.models import Product, Category
    print(f"\nProduct в админке: {Product in site._registry}")
    print(f"Category в админке: {Category in site._registry}")
except Exception as e:
    print(f"Ошибка импорта products: {e}")

try:
    from orders.models import Order
    print(f"Order в админке: {Order in site._registry}")
except Exception as e:
    print(f"Ошибка импорта orders: {e}")

try:
    from reviews.models import Review
    print(f"Review в админке: {Review in site._registry}")
except Exception as e:
    print(f"Ошибка импорта reviews: {e}")

try:
    from cart.models import Cart
    print(f"Cart в админке: {Cart in site._registry}")
except Exception as e:
    print(f"Ошибка импорта cart: {e}")

# Покажем все зарегистрированные модели
print("\n=== ВСЕ ЗАРЕГИСТРИРОВАННЫЕ МОДЕЛИ ===")
for model, model_admin in site._registry.items():
    print(f"- {model._meta.app_label}.{model.__name__}")