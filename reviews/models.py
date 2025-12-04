# reviews/models.py
from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField("Рейтинг", choices=[(i, i) for i in range(1, 6)])
    text = models.TextField("Отзыв", blank=True)
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        unique_together = ('user', 'product')  # один пользователь — один отзыв на товар

    def __str__(self):
        return f"{self.user.username} — {self.rating}★"