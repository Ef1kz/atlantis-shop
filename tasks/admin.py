# tasks/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Task, TaskComment
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status_badge', 'priority_badge',
                    'assigned_to', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'assigned_to', 'due_date']
    search_fields = ['title', 'description', 'assigned_to__username']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Назначение', {
            'fields': ('assigned_to', 'created_by')
        }),
        ('Сроки', {
            'fields': ('due_date', 'completed_at')
        }),
        ('Связанные данные', {
            'fields': ('order',),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_in_progress', 'mark_completed', 'mark_cancelled']

    # Методы для отображения статуса и приоритета с цветными бейджами
    def status_badge(self, obj):
        colors = {
            'new': 'secondary',
            'in_progress': 'warning',
            'completed': 'success',
            'cancelled': 'danger'
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'status'

    def priority_badge(self, obj):
        colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'dark'
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.priority, 'secondary'),
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Приоритет'
    priority_badge.admin_order_field = 'priority'

    # Экшены для быстрого изменения статуса
    def mark_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
        self.message_user(request, f"Задачи переведены в статус 'В работе'")
    mark_in_progress.short_description = "Перевести в 'В работе'"

    def mark_completed(self, request, queryset):
        queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f"Задачи завершены")
    mark_completed.short_description = "Завершить задачи"

    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"Задачи отменены")
    mark_cancelled.short_description = "Отменить задачи"

    # Фильтрация по ролям
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(assigned_to=request.user)
        return qs

    # Добавляем метод для отображения доски
    def changelist_view(self, request, extra_context=None):
        # Группируем задачи по статусам
        tasks_by_status = {
            'new': Task.objects.filter(status='new'),
            'in_progress': Task.objects.filter(status='in_progress'),
            'completed': Task.objects.filter(status='completed'),
            'cancelled': Task.objects.filter(status='cancelled'),
        }

        extra_context = extra_context or {}
        extra_context['tasks_by_status'] = tasks_by_status
        return super().changelist_view(request, extra_context=extra_context)

    @require_POST
    @csrf_exempt
    @staff_member_required
    def change_status(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
            new_status = request.POST.get('status')

            if new_status in dict(Task.TaskStatus.choices):
                task.status = new_status
                task.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('change-status/<int:task_id>/',
                 self.admin_site.admin_view(self.change_status),
                 name='task_change_status'),
        ]
        return custom_urls + urls

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'author', 'created_at', 'text_preview']
    list_filter = ['author', 'created_at']
    readonly_fields = ['created_at']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Предпросмотр'