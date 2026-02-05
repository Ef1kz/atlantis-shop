# atlantis/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from atlantis.admin import admin_site  # ← Импортируем кастомную админку

urlpatterns = [
    # Используем кастомную админку вместо стандартной
    path('admin/', admin_site.urls),  # ← ИЗМЕНЕНО: admin.site.urls -> admin_site.urls

    path('', include('core.urls')),
    path('products/', include(('products.urls', 'products'))),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('api/', include('api.urls')),
    path('accounts/', include('accounts.urls')),

    # Вход/выход через стандартные вьюхи Django
    path('accounts/login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)