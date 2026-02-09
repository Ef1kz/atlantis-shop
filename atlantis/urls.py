# atlantis/urls.py — исправленный главный urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ==================== ОСНОВНОЙ САЙТ (МАГАЗИН) ====================
    path('', include('core.urls')),  # Главная страница магазина
    path('products/', include('products.urls')),  # Каталог товаров
    path('cart/', include('cart.urls')),  # Корзина
    path('accounts/', include('accounts.urls')),  # Регистрация/авторизация

    # ==================== ORDERS (С NAMESPACE) ====================
    path('orders/', include('orders.urls')),  # Заказы - добавлено!

    # ==================== REVIEWS (если есть) ====================
    # path('reviews/', include('reviews.urls')),  # Раскомментируйте если нужно

    # ==================== TASKS URLs (КАНБАН) ВНУТРИ ADMIN ====================
    path('admin/tasks/task/', include('tasks.urls')),

    # ==================== АДМИНКА ====================
    path('admin/', admin.site.urls),
]

# ==================== MEDIA ДЛЯ РАЗРАБОТКИ ====================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)