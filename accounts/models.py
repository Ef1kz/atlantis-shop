# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='Адрес')

    # Убедитесь, что у вас ЕСТЬ или НЕТ это поле:
    # profile_picture = models.ImageField(upload_to='avatars/', blank=True, null=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username