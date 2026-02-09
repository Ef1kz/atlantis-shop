# atlantis/admin.py
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from accounts.models import CustomUser

class AtlantisAdminSite(AdminSite):
    site_header = _('ATLANTIS Администрирование')
    site_title = _('ATLANTIS Admin')
    index_title = _('Панель управления')

    def get_app_list(self, request):
        app_list = super().get_app_list(request)

        # Добавляем ссылку на Kanban доску в меню Tasks
        for app in app_list:
            if app['app_label'] == 'tasks':
                app['models'].append({
                    'name': 'Доска задач',
                    'object_name': 'kanban',
                    'admin_url': '/admin/tasks/task/?view=kanban',
                    'view_only': True,
                })

        return app_list

# Создаем экземпляр кастомной админки
admin_site = AtlantisAdminSite(name='atlantis_admin')

# Регистрируем стандартные модели
admin_site.register(Group, GroupAdmin)
admin_site.register(User, UserAdmin)

# Регистрируем CustomUser
from accounts.admin import CustomUserAdmin
admin_site.register(CustomUser, CustomUserAdmin)

# Регистрируем задачи из нашего кастомного TaskAdmin
try:
    from tasks.models import Task
    from tasks.admin import TaskAdmin  # Импортируем наш кастомный TaskAdmin
    admin_site.register(Task, TaskAdmin)
    print("✅ Task model registered in custom admin")
except ImportError as e:
    print(f"⚠️ Tasks app not found: {e}")