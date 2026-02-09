# tasks/urls.py
from django.urls import path
from . import views

# Уберите app_name если он вызывает конфликт
# app_name = 'tasks'

urlpatterns = [
    path('task/<int:task_id>/detail/', views.task_detail, name='task_detail'),
    path('task/<int:task_id>/update_status/', views.update_status, name='update_status'),
]