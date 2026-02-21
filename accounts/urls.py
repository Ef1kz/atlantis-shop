# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views  # Стандартные views для login/logout
from . import views  # Твой кастомный view для register

app_name = 'accounts'  # Namespace для {% url 'accounts:login' %} и т.д.

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),  # Твой кастомный view
]