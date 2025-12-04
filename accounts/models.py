# accounts/models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('client', 'Клиент'),
        ('designer', 'Дизайнер / B2B'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField("Роль", max_length=20, choices=ROLE_CHOICES, default='client')
    phone = models.CharField("Телефон", max_length=20, blank=True)

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()}"