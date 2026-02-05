# tasks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('change-status/<int:task_id>/', views.change_status, name='task_change_status'),
    path('add/', views.add_task, name='task_add'),
]