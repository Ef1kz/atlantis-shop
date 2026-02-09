# tasks/urls.py
from django.urls import path
from . import views

# УБРАТЬ app_name = 'tasks' - это вызывает конфликт с admin
# или изменить на уникальное имя, например:
app_name = 'tasks_kanban'  # Или вообще удалить app_name

urlpatterns = [
    path('task/<int:task_id>/detail/', views.task_detail, name='task_detail'),
    path('task/<int:task_id>/update_status/', views.update_status, name='update_status'),
    path('test/', views.test_endpoint, name='test'),
    path('test/post/', views.test_post, name='test_post'),
]