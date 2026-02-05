# atlantis/admin.py
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.apps import apps

class AtlantisAdminSite(AdminSite):
    site_header = "ATLANTIS Администрирование"
    site_title = "ATLANTIS Admin"
    index_title = "Корпоративная панель"

    def index(self, request, extra_context=None):
        from tasks.models import Task
        from orders.models import Order

        stats = {
            'new_tasks': Task.objects.filter(status='new').count(),
            'in_progress': Task.objects.filter(status='in_progress').count(),
            'completed': Task.objects.filter(status='completed').count(),
            'today_orders': Order.objects.filter(created_at__date=timezone.now().date()).count(),
        }

        extra_context = extra_context or {}
        extra_context.update(stats)

        return super().index(request, extra_context=extra_context)

admin_site = AtlantisAdminSite(name='admin')

# Автоматическая регистрация всех моделей
for model in apps.get_models():
    try:
        admin_site.register(model)
    except admin.sites.AlreadyRegistered:
        pass