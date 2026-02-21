# tasks/admin.py — полностью корректный и рабочий файл
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from .models import Task, TaskComment


User = get_user_model()

# ==================== ГЛОБАЛЬНАЯ КАСТОМИЗАЦИЯ ADMIN SITE ====================
admin.site.site_header = 'ATLANTIS Администрирование'
admin.site.site_title = 'ATLANTIS Admin'
admin.site.index_title = 'Панель управления'

# КРИТИЧЕСКИ ВАЖНО: Кнопка "Открыть сайт" должна вести на главную страницу магазина
admin.site.site_url = '/'  # ← Это главная страница вашего магазина (core/home.html)


# ==================== РЕДИРЕКТ С /admin/ НА КАНБАН-ДОСКУ ====================
def custom_admin_index(request, extra_context=None):
    """Редирект с главной админки сразу на Kanban-доску"""
    return HttpResponseRedirect('/admin/tasks/task/')

# Переопределяем главную страницу админки
admin.site.index = custom_admin_index


# ==================== ADMIN MODEL ДЛЯ ЗАДАЧ ====================
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'priority', 'assigned_to', 'due_date']
    list_filter = ['status', 'priority', 'assigned_to']
    search_fields = ['title', 'description']
    change_list_template = 'admin/tasks/task/change_list.html'

    def changelist_view(self, request, extra_context=None):
        """Представление списка задач — поддерживает Kanban и табличный вид"""
        extra_context = extra_context or {}
        view_type = request.GET.get('view', 'kanban')
        extra_context['current_view'] = view_type

        if view_type == 'kanban':
            # Получаем все задачи
            all_tasks = Task.objects.select_related('assigned_to').all()
            tasks_by_status = {}

            # Группируем задачи по статусам
            for status_key, status_name in Task.STATUS_CHOICES:
                filtered = all_tasks.filter(status=status_key)
                tasks_by_status[status_key] = {
                    'label': status_name,
                    'count': filtered.count(),
                    'tasks': filtered
                }

            # Передаем данные в контекст
            extra_context.update({
                'tasks_by_status': tasks_by_status,
                'users_list': User.objects.all(),
                'priority_choices': Task.PRIORITY_CHOICES,
                'status_choices': Task.STATUS_CHOICES,
            })

        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        """Добавляем кастомные URL для работы с задачами через модальные окна"""
        urls = super().get_urls()
        custom_urls = [
            path('create_modal/', self.admin_site.admin_view(self.create_task_from_modal)),
            path('<int:task_id>/detail/', self.admin_site.admin_view(self.task_detail)),
            path('<int:task_id>/save_modal/', self.admin_site.admin_view(self.save_task_from_modal)),
            path('<int:task_id>/update_status/', self.admin_site.admin_view(self.update_task_status)),
        ]
        return custom_urls + urls

    # ==================== СОЗДАНИЕ ЗАДАЧИ ====================
    @method_decorator(csrf_exempt)
    def create_task_from_modal(self, request):
        """Создание новой задачи через модальное окно"""
        if request.method == 'POST':
            try:
                # Создаем задачу
                task = Task.objects.create(
                    title=request.POST.get('title'),
                    description=request.POST.get('description', ''),
                    status=request.POST.get('status', 'todo'),
                    priority=request.POST.get('priority', 'medium'),
                    due_date=request.POST.get('due_date') or None,
                    created_by=request.user,
                    assigned_to=User.objects.get(id=request.POST.get('assigned_to')) if request.POST.get('assigned_to') else None,
                )

                # Добавляем комментарий, если есть
                new_comment = request.POST.get('new_comment', '').strip()
                comment_file = request.FILES.get('comment_file')

                if new_comment or comment_file:
                    TaskComment.objects.create(
                        task=task,
                        author=request.user,
                        content=new_comment,
                        attachment=comment_file
                    )

                return JsonResponse({'success': True, 'task_id': task.id})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
        return JsonResponse({'success': False}, status=405)

    # ==================== СОХРАНЕНИЕ ЗАДАЧИ ====================
    @method_decorator(csrf_exempt)
    def save_task_from_modal(self, request, task_id):
        """Сохранение изменений задачи через модальное окно"""
        if request.method == 'POST':
            try:
                task = Task.objects.get(id=task_id)

                # Обновляем поля задачи
                task.title = request.POST.get('title')
                task.description = request.POST.get('description', '')
                task.status = request.POST.get('status')
                task.priority = request.POST.get('priority')

                assigned_id = request.POST.get('assigned_to')
                task.assigned_to = User.objects.get(id=assigned_id) if assigned_id else None

                due_date = request.POST.get('due_date')
                task.due_date = due_date if due_date else None

                task.save()

                # Добавляем новый комментарий, если есть
                new_comment = request.POST.get('new_comment', '').strip()
                comment_file = request.FILES.get('comment_file')

                if new_comment or comment_file:
                    TaskComment.objects.create(
                        task=task,
                        author=request.user,
                        content=new_comment,
                        attachment=comment_file
                    )

                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
        return JsonResponse({'success': False}, status=405)

    # ==================== ОБНОВЛЕНИЕ СТАТУСА (DRAG-AND-DROP) ====================
    @method_decorator(csrf_exempt)
    def update_task_status(self, request, task_id):
        """Обновление статуса задачи при перетаскивании между колонками"""
        try:
            import json
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                new_status = data.get('status')
            else:
                new_status = request.POST.get('status')

            if new_status:
                Task.objects.filter(id=task_id).update(status=new_status)
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Статус не указан'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    # ==================== ДЕТАЛИ ЗАДАЧИ ====================
    def task_detail(self, request, task_id):
        """Получение детальной информации о задаче для модального окна"""
        try:
            task = Task.objects.get(id=task_id)
            return JsonResponse({
                'success': True,
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description or '',
                    'status': task.status,
                    'priority': task.priority,
                    'assigned_to': task.assigned_to.id if task.assigned_to else '',
                    'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else '',
                    'comments': [{
                        'author': str(c.author),
                        'text': c.content,
                        'date': c.created_at.strftime('%d.%m %H:%M'),
                        'file_url': c.attachment.url if c.attachment else None,
                        'file_name': c.attachment.name.split('/')[-1] if c.attachment else None
                    } for c in task.comments.all()]
                }
            })
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Задача не найдена'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== РЕГИСТРАЦИЯ КОММЕНТАРИЕВ ====================
@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['task__title', 'author__username', 'content']
    readonly_fields = ['created_at']

    from django.contrib.auth.models import Group
    from django.contrib.auth.admin import GroupAdmin